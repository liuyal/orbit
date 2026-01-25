# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# app/app_def.py

import json
import os
import pathlib

from dotenv import load_dotenv

from backend.models.projects import Project
from backend.models.schema import pydantic_to_mongo_jsonschema
from backend.models.test_cases import TestCase
from backend.models.test_cycles import TestCycle
from backend.models.test_executions import TestExecution

# Global Constants
API_VERSION = "v1"
DB_NAME = "orbit"

# Directories
ORBIT_ROOT_DIR = pathlib.Path(__file__).parents[2]
ROOT_DIR = pathlib.Path(__file__).parents[1]
TMP_DIR = ROOT_DIR / 'tmp'
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file
if not (ORBIT_ROOT_DIR / 'env' / '.env').exists():
    raise Exception("Environment file .env not found in env directory.")
load_dotenv(ORBIT_ROOT_DIR / 'env' / '.env')

# TM DB Collections
DB_COLLECTION_PRJ = "projects"
DB_COLLECTION_TC = "test-cases"
DB_COLLECTION_TE = "test-executions"
DB_COLLECTION_TCY = "test-cycles"

# TM DB Keys Prefixes
TC_KEY_PREFIX = "T"
TE_KEY_PREFIX = "E"
TCY_KEY_PREFIX = "C"

# MongoDB Schemas
PROJECT_SCHEMA = pydantic_to_mongo_jsonschema(Project.model_json_schema())
TEST_CASE_SCHEMA = pydantic_to_mongo_jsonschema(TestCase.model_json_schema())
TEST_EXECUTION_SCHEMA = pydantic_to_mongo_jsonschema(TestExecution.model_json_schema())
TEST_CYCLE_SCHEMA = pydantic_to_mongo_jsonschema(TestCycle.model_json_schema())

DB_COLLECTIONS = [
    (DB_COLLECTION_PRJ, PROJECT_SCHEMA),
    (DB_COLLECTION_TC, TEST_CASE_SCHEMA),
    (DB_COLLECTION_TE, TEST_EXECUTION_SCHEMA),
    (DB_COLLECTION_TCY, TEST_CYCLE_SCHEMA)
]

# MongoDB Connection Details
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_USER = os.getenv("MONGODB_USER", "admin")
MONGODB_PASS = os.getenv("MONGODB_PASS", "password")

MONGODB_URL = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}"

# SQLite Constants
SQLITE_DATABASE = os.getenv("SQLITE_DATABASE")

# GitHub Configuration Constants
GITHUB_API_URL = os.getenv("GITHUB_API_URL")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = json.loads(os.getenv("GITHUB_REPOSITORY"))

# Runner Constants
QUERY_API_INTERVAL = 60
TABLE_TIMESTAMP_STATS = "timestamp-stats"
TABLE_RUNNER_STATS_HISTORIC = "runner-stats-historic"
TABLE_RUNNER_STATS_CURRENT = "runner-stats-current"
TABLE_RUNNERS_BUSY_STATS = "runners-busy-stats"
TABLE_RUNNERS_BUSY_STATS_BY_JOB = "runners-busy-stats-by-job"
TABLE_RUNNERS_ONLINE_STATS = "runners-online-stats"
TABLE_USER_LEADERBOARD_STATS = "user-leaderboard-stats"
