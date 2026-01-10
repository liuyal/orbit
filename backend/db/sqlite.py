# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# db/sqlitedb.py

import os
import pathlib
import sqlite3

from backend.app_def.app_def import (
    DB_NAME
)
from backend.db.db import (
    DatabaseClient,
    DBType,
    DBMode
)

SQLITE_DATABASE = os.getenv("SQLITE_DATABASE")


class SqliteClient(DatabaseClient):

    def __init__(self,
                 db_name: str = DB_NAME,
                 db_url: str = SQLITE_DATABASE,
                 db_type: DBType = DBType.SQLITE,
                 db_mode: DBMode = DBMode.DEBUG):
        """ Initialize the Sqlite client. """

        super().__init__(db_name, db_url, db_type, db_mode)

        self._db_conn = None

    @property
    def db_conn(self):
        """ Get the database connection. """
        return self._db_conn

    async def connect(self):
        """Get the client with optional authentication."""

        if self.db_url is None:
            self.db_url = pathlib.Path(__file__).parent / 'tmp' / f"{self.db_name}.db"

        db_path = pathlib.Path(self.db_url)

        # Check path existence, create if not exists
        if not db_path.parent.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connect to the database
        if not db_path.exists():
            # Create the database file
            self._db_conn = sqlite3.connect(str(db_path))
            self._db_conn.close()

        # Reconnect in read-only mode
        self._db_conn = sqlite3.connect(f"file:{str(db_path)}?mode=ro", uri=True)

    async def close(self):
        """ Disconnect from the database. """

        if self._db_conn:
            self._db_conn.close()

    async def configure(self,
                        **kwargs) -> None:
        """Configure database connection parameters"""

        # Drop the database if in debug mode
        # clean_db = "clean_db" in kwargs and kwargs["clean_db"]
        # if clean_db:
        # self._db_conn.execute("")

    async def create(self,
                     table: str,
                     data: dict) -> bool:
        """Insert a new record into the database."""

    async def find(self,
                   table: str,
                   query: dict) -> list:
        """Retrieve records from the database."""

    async def find_one(self,
                       table: str,
                       query: dict) -> dict:
        """Retrieve a single record from the database."""

    async def update(self,
                     table: str,
                     query: dict,
                     update_data: dict) -> tuple:
        """Update records in the database."""

    async def delete(self,
                     table: str,
                     query: dict) -> tuple:
        """Delete records from the database."""

    async def delete_one(self,
                         table: str,
                         query: dict) -> tuple:
        """Delete records from the database."""

    async def execute_raw(self,
                          command,
                          *args,
                          **kwargs):
        """ Execute a raw query or command
            (SQL for SQLite, command for MongoDB).
        """
