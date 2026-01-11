# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import pathlib

API_VERSION = "v1"
DB_NAME = "orbit"

# TM DB Collections
DB_COLLECTION_PRJ = "projects"
DB_COLLECTION_TC = "test-cases"
DB_COLLECTION_TE = "test-executions"
DB_COLLECTION_TCY = "test-cycles"

# TM DB Keys Prefixes
TC_KEY_PREFIX = "T"
TE_KEY_PREFIX = "E"
TCY_KEY_PREFIX = "C"

# Directories
TMP_DIR = pathlib.Path(__file__).parents[1] / 'tmp'
TMP_DIR.mkdir(parents=True, exist_ok=True)
