# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging
import os
import pathlib
import sqlite3
import time

import requests
from natsort import natsorted

# GitHub Configuration
GITHUB_API_URL = os.getenv("GITHUB_API_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Workflow Repositories
# GITHUB_WORKFLOW_REPOS = ["test-workflows-libra"]
# RESO_WORKFLOW_PATH = ".github/workflows/reso-workflow.yml"

GITHUB_WORKFLOW_REPOS = ["workflow-test"]
RESO_WORKFLOW_PATH = ".github/workflows/blank.yml"

# Tables definition
TABLE_RUNNER_STATS_HISTORIC = "RUNNER_STATS_HISTORIC"
TABLE_RUNNER_STATS_CURRENT = "RUNNER_STATS_CURRENT"
TABLE_RUNNERS_BUSY_STATS = "RUNNERS_BUSY_STATS"
TABLE_RUNNERS_BUSY_STATS_BY_JOB = "RUNNERS_BUSY_STATS_BY_JOB"
TABLE_RUNNERS_ONLINE_STATS = "RUNNERS_ONLINE_STATS"
TABLE_USER_LEADERBOARD_STATS = "USER_LEADERBOARD_STATS"
TABLE_TIMESTAMP_STATS = "TIMESTAMP_STATS"


def get_runner_usage_stats(db_conn: sqlite3.Connection):
    """ get the runner usage stats from db file """

    cursor = db_conn.cursor()

    cursor.execute(f"SELECT name, busy_count, idle_count FROM {TABLE_RUNNERS_BUSY_STATS};")
    runners_busy_stats = cursor.fetchall()

    cursor.execute(f"SELECT name, reso_count, test_count FROM {TABLE_RUNNERS_BUSY_STATS_BY_JOB};")
    runners_busy_by_job = cursor.fetchall()

    busy_stats = {}
    for name, busy, idle in runners_busy_stats:
        busy_stats[name] = (busy / (busy + idle), idle / (busy + idle))

    busy_job_stats = {}
    for name, reso_count, test_count in runners_busy_by_job:
        busy_job_stats[name] = {"RESO": reso_count, "TEST_RUN": test_count}

    busy_stats = dict(natsorted(busy_stats.items()))
    busy_job_stats = dict(natsorted(busy_job_stats.items()))

    return busy_stats, busy_job_stats


def get_runner_uptime_stats(db_conn: sqlite3.Connection):
    """ get the runner uptime stats from db file """

    cursor = db_conn.cursor()
    cursor.execute(f"SELECT name, online_count, offline_count FROM {TABLE_RUNNERS_ONLINE_STATS};")
    runners_online_stats = cursor.fetchall()

    online_stats = {}
    for name, online_count, offline_count in runners_online_stats:
        online_stats[name] = (online_count / (online_count + offline_count),
                              offline_count / (online_count + offline_count))

    online_stats = dict(natsorted(online_stats.items()))

    return online_stats


def get_leaderboard_stats(db_conn: sqlite3.Connection):
    """ get the user usage hours stats from db file """

    cursor = db_conn.cursor()
    cursor.execute(f"SELECT user, use_time, job_type FROM {TABLE_USER_LEADERBOARD_STATS};")
    user_stats = cursor.fetchall()

    user_usage = {}
    user_order = {}
    for name, ts, job_type in user_stats:
        if name not in user_usage:
            user_usage[name] = {}
            user_usage[name]['RESO'] = 0
            user_usage[name]['TEST_RUN'] = 0

        if name not in user_order:
            user_order[name] = 0

        user_order[name] += ts
        user_usage[name][job_type] = ts

    # Sort user by total time
    user_order = dict(sorted(user_order.items(), key=lambda item: item[1], reverse=True))

    return user_usage, user_order


def get_timestamps_stats(db_conn: sqlite3.Connection):
    """ get the timestamp stats from db file """

    cursor = db_conn.cursor()
    cursor.execute(f"SELECT start_ts, end_ts FROM {TABLE_TIMESTAMP_STATS};")
    timestamps = cursor.fetchone()

    return timestamps


def get_github_runners(repo: str):
    """ get github runners info """

    resp = requests.get(url=f"{GITHUB_API_URL}/{repo}/actions/runners",
                        headers={'Authorization': f'bearer {GITHUB_TOKEN}'},
                        params={"per_page": 100})

    if resp.status_code != 200:
        logging.debug(resp.content)
        return []

    return resp.json()["runners"]


def get_github_jobs(repo: str):
    """ get libra workflow running jobs """

    params = {"per_page": 100, "status": "in_progress"}
    resp = requests.get(url=f"{GITHUB_API_URL}/{repo}/actions/runs",
                        headers={'Authorization': f'bearer {GITHUB_TOKEN}'},
                        params=params)

    if resp.status_code != 200:
        logging.debug(resp.content)
        return []

    jobs = resp.json()["workflow_runs"]
    running_jobs = []
    for job in jobs:
        resp = requests.get(url=job["jobs_url"],
                            headers={'Authorization': f'bearer {GITHUB_TOKEN}'},
                            params=params)

        if resp.status_code != 200:
            logging.debug(resp.content)

        job["job_type"] = "TEST_RUN"
        if job["path"] == RESO_WORKFLOW_PATH:
            job["job_type"] = "RESO"

        data = resp.json()["jobs"]
        for item in data:
            item.update(job)

        running_jobs += data

    return running_jobs


def convert_sqlite_type(input_type):
    """ Convert python types to sqlite types """

    type_mapping = {int: 'INTEGER',
                    float: 'REAL',
                    str: 'VARCHAR(255)',
                    bytes: 'BLOB',
                    bool: 'INTEGER'}

    return type_mapping.get(input_type, 'VARCHAR(255)')


def query_runner_status(db_file: pathlib.Path,
                        interval: int = 60):
    """ get runner status from github """

    try:
        # Get runner status from GitHub APIs
        logging.debug(f"Getting runner status...")
        runners_data = []
        jobs_data = []
        start_ts = time.time()
        for repo in GITHUB_WORKFLOW_REPOS:
            runners_data += get_github_runners(repo)
            jobs_data += get_github_jobs(repo)
        logging.debug(f"Query completed in {round(time.time() - start_ts, 2)} seconds")

        # Process runner data
        ts = int(time.time())
        for runner in runners_data:
            # Add extra fields
            runner["ts"] = ts
            runner["job"] = "-"
            runner["job_type"] = "-"
            runner["user"] = "-"

            if runner['busy']:
                # Runner is currently running a job
                for job in jobs_data:
                    # Find the job assigned to this runner
                    if job['runner_id'] == runner['id']:
                        runner["job"] = job["html_url"]
                        runner["user"] = job["triggering_actor"]["login"]
                        runner["job_type"] = job["job_type"]
                        break

            # Get runner designation from labels
            runner["designation"] = "-"
            runner_labels = runner.pop("labels")
            for item in runner_labels:
                if "type:" in item["name"]:
                    runner["designation"] = item["name"].split(":")[-1]
                    break

        # Create DB connection
        db_conn = sqlite3.connect(db_file)
        cursor = db_conn.cursor()

        # Get field names and types
        fieldnames = list(runners_data[0].keys())
        fieldnames.sort()

        # Create table columns with db types
        columns = []
        columns_types = []
        for item in fieldnames:
            sq_type = convert_sqlite_type(type(runners_data[0][item]))
            columns.append(f"{item}")
            columns_types.append(f"{item} {sq_type}")
        num_columns = f"{len(columns) * '?, '}".strip().strip(',')
        columns_types = ', '.join(columns_types)
        columns = ', '.join(columns)

        # Save running stats into historic runners_stats table
        logging.debug("Saving runner stats...")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_RUNNER_STATS_HISTORIC} ({columns_types})")
        # Insert data
        insert_cmd = f"INSERT INTO {TABLE_RUNNER_STATS_HISTORIC} ({columns}) VALUES ({num_columns})"
        for runner in runners_data:
            cursor.execute(insert_cmd, [runner[item] for item in fieldnames])

        # Save to current runner stats table
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_RUNNER_STATS_CURRENT};")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_RUNNER_STATS_CURRENT} ({columns_types})")
        # Insert data
        insert_cmd = f"INSERT INTO {TABLE_RUNNER_STATS_CURRENT} ({columns}) VALUES ({num_columns})"
        for runner in runners_data:
            cursor.execute(insert_cmd, [runner[item] for item in fieldnames])

        # Get runner utilization stats
        logging.debug("Calculating runner utilization stats...")
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_RUNNERS_BUSY_STATS};")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_RUNNERS_BUSY_STATS} "
                       "(name VARCHAR(255), busy_count REAL, idle_count REAL);")
        cursor.execute(f"""
           INSERT INTO {TABLE_RUNNERS_BUSY_STATS} (name, busy_count, idle_count)
           SELECT
           name,
           SUM(CASE WHEN busy = 1 THEN 1 ELSE 0 END) AS busy_count,
           SUM(CASE WHEN busy = 0 THEN 1 ELSE 0 END) AS idle_count
           FROM {TABLE_RUNNER_STATS_HISTORIC}
           GROUP BY name;""")

        # Get runner busy by job type stats
        logging.debug("Calculating runner busy by job type stats...")
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_RUNNERS_BUSY_STATS_BY_JOB};")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_RUNNERS_BUSY_STATS_BY_JOB} "
                       "(name VARCHAR(255), reso_count REAL, test_count REAL);")
        cursor.execute(f"""
            INSERT INTO {TABLE_RUNNERS_BUSY_STATS_BY_JOB} (name, reso_count, test_count)
            SELECT
            name,
            SUM(CASE WHEN busy = 1 AND job_type = 'RESO' THEN 1 ELSE 0 END) AS reso_count,
            SUM(CASE WHEN busy = 1 AND job_type = 'TEST_RUN' THEN 1 ELSE 0 END) AS test_count
            FROM {TABLE_RUNNER_STATS_HISTORIC}
            GROUP BY name;""")

        # Get online percentage stats
        logging.debug("Calculating runner online stats...")
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_RUNNERS_ONLINE_STATS};")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_RUNNERS_ONLINE_STATS} "
                       "(name VARCHAR(255), online_count REAL, offline_count REAL);")
        cursor.execute(f"""
            INSERT INTO {TABLE_RUNNERS_ONLINE_STATS} (name, online_count, offline_count)
            SELECT
            name,
            SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) AS online_count,
            SUM(CASE WHEN status = 'offline' THEN 1 ELSE 0 END) AS offline_count
            FROM {TABLE_RUNNER_STATS_HISTORIC}
            GROUP BY name;""")

        # Save user usage info
        logging.debug("Calculating user leaderboard stats...")
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_USER_LEADERBOARD_STATS};")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_USER_LEADERBOARD_STATS} "
                       f"(user VARCHAR(255), "
                       f"job_type VARCHAR(255), use_time REAL);")
        cursor.execute(f"""
            INSERT INTO {TABLE_USER_LEADERBOARD_STATS} (user, job_type, use_time)
            SELECT user, job_type, COUNT(*) AS use_time
            FROM {TABLE_RUNNER_STATS_HISTORIC}
            WHERE user != '-'
            GROUP BY user, job_type
            ORDER BY user DESC, use_time DESC;""")

        # Save elapsed ts info
        logging.debug("Saving timestamps...")
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_TIMESTAMP_STATS};")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_TIMESTAMP_STATS} "
                       f"(start_ts REAL, end_ts REAL);")
        cursor.execute(f"""
            INSERT INTO {TABLE_TIMESTAMP_STATS} (start_ts, end_ts)
            SELECT MAX(ts) AS start_ts, MIN(ts) AS end_ts
            FROM {TABLE_RUNNER_STATS_HISTORIC};""")

        # Commit and close DB connection
        db_conn.commit()
        db_conn.close()

    except Exception as err:
        logging.warning(f"Exception occurred {err}",
                        exc_info=True)

    logging.debug(f"Sleeping for {interval} seconds...")
    # time.sleep(interval)
