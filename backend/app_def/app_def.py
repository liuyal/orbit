# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import keyring

API_VERSION = "v1"

DB_NAME = "orbit"

# TM DB Collections
DB_COLLECTION_PRJ = "projects"
DB_COLLECTION_TC = "test-cases"
DB_COLLECTION_TE = "test-executions"
DB_COLLECTION_TCY = "test-cycles"

TC_KEY_PREFIX = "T"
TE_KEY_PREFIX = "E"
TCY_KEY_PREFIX = "C"

# GitHub Enterprise Configuration
GITHUB_API_URL = "https://github.schneider-electric.com/api/v3/repos/SchneiderProsumer"
GITHUB_API_TOKEN = keyring.get_password("GHE_PAT", "GHE_PAT_USER")
HEADER = {'Authorization': f'bearer {GITHUB_API_TOKEN}'}
WORKFLOW_REPOS = ["test-workflows-libra"]

# Runners DB File
RUNNERS_DB_FILE = "runners.db"
