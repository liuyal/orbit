# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# app/app_def.py

import os
import pathlib
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

from backend.models.projects import Project
from backend.models.schema import pydantic_to_mongo_jsonschema
from backend.models.test_cases import TestCase
from backend.models.test_cycles import TestCycle
from backend.models.test_executions import TestExecution


@dataclass
class DBCollection:
    name: str
    schema: Optional[dict] = field(default_factory=dict)


@dataclass
class DB:
    name: str
    collections: list[DBCollection]


# Global Constants
API_VERSION = "v1"

# Directories
ORBIT_ROOT_DIR = pathlib.Path(__file__).parents[2]
ROOT_DIR = pathlib.Path(__file__).parents[1]
TMP_DIR = ROOT_DIR / 'tmp'
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file
if not (ORBIT_ROOT_DIR / 'env' / '.env').exists():
    raise Exception("Environment file .env not found in env directory.")
load_dotenv(ORBIT_ROOT_DIR / 'env' / '.env')

# GitHub Configuration Constants
GITHUB_API_URL = os.getenv("GITHUB_API_URL").strip()
GITHUB_OWNER = os.getenv("GITHUB_OWNER").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN").strip()
GITHUB_REPOSITORY = [m.strip() for m in os.getenv("GITHUB_REPOSITORY").split(",")]

# MongoDB Connection Details
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost").strip()
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017").strip()
MONGODB_USER = os.getenv("MONGODB_USER", "admin").strip()
MONGODB_PASS = os.getenv("MONGODB_PASS", "password").strip()
MONGODB_URL = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}"

# Runner Constants
API_QUERY_INTERVAL = 60
RUNNER_STATUS_CACHE = "runner_status_cache"

# DB TM Prefixes
TC_KEY_PREFIX = "T"
TE_KEY_PREFIX = "E"
TCY_KEY_PREFIX = "C"

# DB Schemas
PROJECT_SCHEMA = pydantic_to_mongo_jsonschema(Project.model_json_schema())
TEST_CASE_SCHEMA = pydantic_to_mongo_jsonschema(TestCase.model_json_schema())
TEST_EXECUTION_SCHEMA = pydantic_to_mongo_jsonschema(TestExecution.model_json_schema())
TEST_CYCLE_SCHEMA = pydantic_to_mongo_jsonschema(TestCycle.model_json_schema())

# DB COLLECTIONS - TM
DB_COLLECTION_TM_PRJ = DBCollection(name="projects", schema=PROJECT_SCHEMA)
DB_COLLECTION_TM_TC = DBCollection(name="test-cases", schema=TEST_CASE_SCHEMA)
DB_COLLECTION_TM_TE = DBCollection(name="test-executions", schema=TEST_EXECUTION_SCHEMA)
DB_COLLECTION_TM_TCY = DBCollection(name="test-cycles", schema=TEST_CYCLE_SCHEMA)

# DB COLLECTIONS - RUNNER
DB_COLLECTION_RUNNERS_TIMESTAMP_STATS = DBCollection(name="timestamp-stats")
DB_COLLECTION_RUNNERS_STATS_HISTORIC = DBCollection(name="runner-stats-historic")
DB_COLLECTION_RUNNERS_STATS_CURRENT = DBCollection(name="runner-stats-current")
DB_COLLECTION_RUNNERS_BUSY_STATS = DBCollection(name="runners-stats-busy")
DB_COLLECTION_RUNNERS_BUSY_STATS_BY_JOB = DBCollection(name="runners-stats-busy-by-job")
DB_COLLECTION_RUNNERS_ONLINE_STATS = DBCollection(name="runners-stats-online")
DB_COLLECTION_USER_LEADERBOARD_STATS = DBCollection(name="user-leaderboard-stats")

# DB Constants
DB_NAME = "ORBIT"
DB_NAME_TM = DB(
    name=f"{DB_NAME}-TM",
    collections=[
        DB_COLLECTION_TM_PRJ,
        DB_COLLECTION_TM_TC,
        DB_COLLECTION_TM_TE,
        DB_COLLECTION_TM_TCY
    ]
)

DB_NAME_RUNNERS = DB(
    name=f"{DB_NAME}-RUNNERS",
    collections=[
        DB_COLLECTION_RUNNERS_TIMESTAMP_STATS,
        DB_COLLECTION_RUNNERS_STATS_HISTORIC,
        DB_COLLECTION_RUNNERS_STATS_CURRENT,
        DB_COLLECTION_RUNNERS_BUSY_STATS,
        DB_COLLECTION_RUNNERS_BUSY_STATS_BY_JOB,
        DB_COLLECTION_RUNNERS_ONLINE_STATS,
        DB_COLLECTION_USER_LEADERBOARD_STATS
    ]
)

# DB Mapping
DB_ALL = [DB_NAME_TM, DB_NAME_RUNNERS]
