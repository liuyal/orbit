# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# db/db.py

from abc import ABC, abstractmethod
from enum import Enum


class DBType(Enum):
    """ Enumeration for supported database types. """

    MONGODB = 'mongodb'


class DBMode(Enum):
    """ Enumeration for supported database op mode. """

    DEBUG = 0
    RELEASE = 1


class DatabaseClient(ABC):
    """ Abstract base class for database implementations supporting SQLite and MongoDB. """

    def __init__(self,
                 db_name: str,
                 db_url: str,
                 db_type: DBType,
                 db_mode: DBMode):
        """ Initialize the database client."""

        self._db_name = db_name
        self._db_url = db_url
        self._db_type = db_type
        self._db_mode = db_mode
        self._db_client = None

    @property
    def db_type(self) -> DBType:
        """ Get the database type. """
        return self._db_type

    @property
    def db_name(self) -> str:
        """ Get the database name. """
        return self._db_name

    @property
    def db_url(self) -> str:
        """ Get the database URL or file path. """
        return self._db_url

    @property
    def db_mode(self) -> DBMode:
        """ Get the database mode. """
        return self._db_mode

    @property
    def db_client(self):
        """ Get the underlying database client/connection. """
        return self._db_client

    @db_type.setter
    def db_type(self, db_type: DBType):
        """ Set the database type. """
        self._db_type = db_type

    @db_name.setter
    def db_name(self, db_name: str):
        """ Set the database name. """
        self._db_name = db_name

    @db_url.setter
    def db_url(self, db_url: str):
        """ Set the database URL or file path. """
        self._db_url = db_url

    @db_mode.setter
    def db_mode(self, db_mode: DBMode):
        """ Set the database mode. """
        self._db_mode = db_mode

    @abstractmethod
    def configure(self, **kwargs):
        """ Configure database connection & init parameters """

    @abstractmethod
    def connect(self):
        """ Connect to the database. """

    @abstractmethod
    def close(self):
        """ Disconnect from the database. """

    @abstractmethod
    def create(self, table: str, data: dict):
        """Insert a new record into the database."""

    @abstractmethod
    def find(self, table: str, query: dict):
        """Retrieve records from the database."""

    @abstractmethod
    def find_one(self, table: str, query: dict):
        """Retrieve records from the database."""

    @abstractmethod
    def update(self, table: str, query: dict, data: dict):
        """Update records in the database."""

    @abstractmethod
    def delete(self, table: str, query: dict):
        """Delete records from the database."""

    @abstractmethod
    def delete_one(self, table: str, query: dict):
        """Delete records from the database."""

    @abstractmethod
    def execute_raw(self, command, *args, **kwargs):
        """ Execute a raw query or command
            (SQL for SQLite, command for MongoDB).
        """
