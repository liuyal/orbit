# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import asyncio
import logging
import time

import requests

from backend.app.app_def import (
    GITHUB_API_URL,
    GITHUB_OWNER,
    GITHUB_TOKEN,
    GITHUB_REPOSITORY,
    TABLE_RUNNER_STATS_HISTORIC,
    TABLE_RUNNER_STATS_CURRENT
)
from backend.db.mongodb import MongoClient
from backend.models.runner import Runner


def query_github_runners(repo: str):
    """ get github runners info """

    # Get all self-hosted runners for the repository
    resp = requests.get(url=f"{GITHUB_API_URL}/{GITHUB_OWNER}/{repo}/actions/runners",
                        headers={'Authorization': f'bearer {GITHUB_TOKEN}'},
                        params={"per_page": 100})

    # Check for request success
    if resp.status_code != 200:
        logging.debug(resp.content)
        return []

    return resp.json()["runners"]


def query_github_jobs(repo: str):
    """ get workflow in_progress jobs """

    # Define parameters to filter for in_progress workflow runs
    params = {"per_page": 100, "status": "in_progress"}

    # Get all in_progress workflow runs
    resp = requests.get(url=f"{GITHUB_API_URL}/{GITHUB_OWNER}/{repo}/actions/runs",
                        headers={'Authorization': f'bearer {GITHUB_TOKEN}'},
                        params=params)

    # Check for request success
    if resp.status_code != 200:
        logging.warning(resp.content)
        return []

    jobs = resp.json()["workflow_runs"]
    running_jobs = []
    for job in jobs:
        resp = requests.get(url=job["jobs_url"],
                            headers={'Authorization': f'bearer {GITHUB_TOKEN}'},
                            params=params)

        if resp.status_code != 200:
            logging.debug(resp.content)

        # Append job info to each job item
        data = resp.json()["jobs"]
        for item in data:
            item.update(job)

        running_jobs += data

    return running_jobs


def fetch_runner_status():
    """ fetch runner status from github """

    try:
        # Get runner status from GitHub APIs
        logging.debug(f"Getting runner status...")

        runners = []
        jobs = []
        ts = time.time()
        for repo in GITHUB_REPOSITORY:
            runners += query_github_runners(repo)
            jobs += query_github_jobs(repo)

        logging.info(f"Runner status query completed in {round(time.time() - ts, 2)} seconds")

        # Process runner data
        for runner in runners:
            # Add info fields
            runner["queried_ts"] = int(ts)

            # Get runner designation from labels
            runner["designation"] = "-"
            runner_labels = runner.get("labels", [])
            for item in runner_labels:
                if "type:" in item["name"]:
                    runner["designation"] = item["name"].split(":")[-1]
                    break

            if runner["busy"]:
                # Runner is currently running a job
                # Find the job assigned to this runner
                for job in jobs:
                    if job['runner_id'] == runner['id']:
                        runner["job"] = job["path"]
                        runner["job_url"] = job["html_url"]
                        runner["user"] = job["triggering_actor"]["login"]
                        break

            else:
                # Runner is idle
                runner["job"] = "-"
                runner["job_url"] = "-"
                runner["user"] = "-"

        return runners

    except Exception as err:
        logging.warning(f"Exception occurred {err}", exc_info=True)
        return []


async def save_runner_status(mdb: MongoClient, interval: int = 60):
    """ save runner status to mongodb - runs periodically in background """

    while True:
        try:
            # Fetch runner status from GitHub
            status = fetch_runner_status()

            # Clear the current stats collection before inserting new data
            await mdb.delete(TABLE_RUNNER_STATS_CURRENT, {})

            # Save runner status to historic and current collections
            for item in status:
                db_insert = Runner(**item).model_dump()
                await mdb.create(TABLE_RUNNER_STATS_HISTORIC, db_insert)
                await mdb.create(TABLE_RUNNER_STATS_CURRENT, db_insert)

            logging.debug(f"Saved {len(status)} runner statuses to database")

        except Exception as e:
            logging.error(f"Error saving runner status: {e}", exc_info=True)

        # Use asyncio.sleep instead of time.sleep to not block event loop
        await asyncio.sleep(interval)
