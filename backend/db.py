# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# db.py

import os

from motor.motor_asyncio import AsyncIOMotorClient

DB_NAME = "orbit"

MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_USER = os.getenv("MONGODB_USER", "admin")
MONGODB_PASS = os.getenv("MONGODB_PASS", "password")

MONGODB_URL = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}"


def get_db_client():
    """Get the MongoDB client with optional authentication."""

    return AsyncIOMotorClient(MONGODB_URL)
