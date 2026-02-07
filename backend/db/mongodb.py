# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# db/mongodb.py

import logging

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from backend.app.app_def import (
    DB_NAME,
    MONGODB_URL,
    MONGODB_HOST,
    MONGODB_PORT,
    MONGODB_USER,
    DB_COLLECTIONS
)
from backend.db.db import (
    DatabaseClient,
    DBType,
    DBMode
)


class MongoClient(DatabaseClient):

    def __init__(self,
                 db_name: str = DB_NAME,
                 db_url: str = MONGODB_URL,
                 db_type: DBType = DBType.MONGODB,
                 db_mode: DBMode = DBMode.DEBUG):
        """ Initialize the MongoDB client. """

        super().__init__(db_name, db_url, db_type, db_mode)

    def _convert_object_id(self, doc: dict) -> dict:
        """Convert ObjectId to string in a MongoDB document."""

        if doc and "_id" in doc and isinstance(doc["_id"], ObjectId):
            doc["_id"] = str(doc["_id"])

        return doc

    async def connect(self):
        """Get the MongoDB client with optional authentication."""

        logging.info(f"Connecting to MongoDB "
                     f"at {MONGODB_HOST}:{MONGODB_PORT} "
                     f"with user '{MONGODB_USER}'")

        self._db_client = AsyncIOMotorClient(self._db_url)

    async def close(self):
        """ Disconnect from the database. """

        logging.info(f"Closing MongoDB connection "
                     f"at {MONGODB_HOST}:{MONGODB_PORT}")

        if self._db_client is not None:
            self._db_client.close()

    async def configure(self,
                        **kwargs) -> None:
        """Configure database connection parameters"""

        # Drop the database if in debug mode
        clean_db = "clean_db" in kwargs and kwargs["clean_db"]
        if clean_db:
            await self._db_client.drop_database(self._db_name)

        # Initialize the database
        if self._db_name not in await self._db_client.list_database_names():
            await self._db_client[self._db_name].drop_collection("init")
            await self._db_client[self._db_name].create_collection("init")

        # Initialize required collections
        collections = await self._db_client[self._db_name].list_collection_names()
        for collection, schema in DB_COLLECTIONS:
            if collection not in collections:
                await self._db_client[self._db_name].create_collection(collection,
                                                                       validator={"$jsonSchema": schema})

    async def create(self,
                     table: str,
                     data: dict) -> bool:
        """Insert a new record into the database."""

        await self._db_client[self._db_name][table].insert_one(data)

        return True

    async def find(self,
                   table: str,
                   query: dict) -> list:
        """Retrieve records from the database."""

        cursor = self._db_client[self._db_name][table].find(query)
        results = await cursor.to_list()
        results = [self._convert_object_id(p) for p in results]

        return results

    async def find_one(self,
                       table: str,
                       query: dict) -> dict:
        """Retrieve a single record from the database."""

        result = await self._db_client[self._db_name][table].find_one(query)
        result = self._convert_object_id(result)

        return result

    async def update(self,
                     table: str,
                     data: dict,
                     query: dict ) -> tuple:
        """Update records in the database."""

        result = await self._db_client[self._db_name][table].update_many(query,
                                                                         {"$set": data})
        return result, result.matched_count

    async def delete(self,
                     table: str,
                     query: dict) -> tuple:
        """Delete records from the database."""

        result = await self._db_client[self._db_name][table].delete_many(query)

        return result, result.deleted_count

    async def delete_one(self,
                         table: str,
                         query: dict) -> tuple:
        """Delete records from the database."""

        result = await self._db_client[self._db_name][table].delete_one(query)

        return result, result.deleted_count

    async def execute_raw(self,
                          command,
                          *args,
                          **kwargs):
        """ Execute a raw query or command
            (SQL for SQLite, command for MongoDB).
        """
