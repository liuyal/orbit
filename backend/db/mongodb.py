# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# db/mongodb.py

import asyncio
import logging

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from backend.app.app_def import (
    MONGODB_URL,
    MONGODB_HOST,
    MONGODB_PORT,
    MONGODB_USER,
    DB_ALL
)
from backend.db.db import (
    DatabaseClient,
    DBType,
    DBMode
)


class MongoClient(DatabaseClient):

    def __init__(self,
                 db_url: str = MONGODB_URL,
                 db_type: DBType = DBType.MONGODB,
                 db_mode: DBMode = DBMode.DEBUG):
        """ Initialize the MongoDB client. """

        super().__init__(db_url, db_type, db_mode)

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

        self._db_client = AsyncIOMotorClient(self._db_url, maxPoolSize=50)

    async def close(self):
        """ Disconnect from the database. """

        logging.info(f"Closing MongoDB connection "
                     f"at {MONGODB_HOST}:{MONGODB_PORT}")

        if self._db_client is not None:
            self._db_client.close()

    async def configure(self, **kwargs) -> None:
        """Configure database connection parameters.

        Retries up to 3 times with brief backoff to survive the transient
        AutoReconnect that MongoDB sometimes raises immediately after a
        drop_database while the server re-establishes internal state.
        """

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                await self._configure(**kwargs)
                return

            except Exception as e:
                if attempt == max_attempts:
                    raise

                wait = attempt * 0.5
                logging.warning(f"configure() attempt {attempt} failed ({e}); "
                                f"retrying in {wait}s…")

                await asyncio.sleep(wait)

    async def _configure(self, **kwargs) -> None:
        """Internal configure implementation (called by configure with retry)."""

        if "clean_db" in kwargs:
            for db in kwargs["clean_db"]:
                # Clean up database
                await self._db_client.drop_database(db.name)

        for db in DB_ALL:
            # Initialize the database
            if db.name not in await self._db_client.list_database_names():
                await self._db_client[db.name].drop_collection("init")
                await self._db_client[db.name].create_collection("init")

            # Initialize required collections
            collections = await self._db_client[db.name].list_collection_names()

            # create collections with schema validation if not exist
            for collection in db.collections:
                if collection.name not in collections:
                    await self._db_client[db.name].create_collection(
                        collection.name,
                        validator={"$jsonSchema": collection.schema}
                    )

                if collection.index:
                    await self._db_client[db.name][collection.name].create_index(
                        keys=collection.index.keys,
                        name=collection.index.index_name,
                        unique=True
                    )

    async def create(self,
                     db_name: str,
                     table: str,
                     data: dict) -> bool:
        """Insert a new record into the database."""

        await self._db_client[db_name][table].insert_one(data)

        return True

    async def count(self,
                    db_name: str,
                    table: str,
                    query: dict) -> int:
        """Count records in the database matching the query."""

        return await self._db_client[db_name][table].count_documents(query)

    async def find(self,
                   db_name: str,
                   table: str,
                   query: dict,
                   projection: dict = None) -> list:
        """Retrieve records from the database."""

        cursor = self._db_client[db_name][table].find(query, projection)
        results = await cursor.to_list()
        results = [self._convert_object_id(p) for p in results]

        return results

    async def find_one(self,
                       db_name: str,
                       table: str,
                       query: dict) -> dict:
        """Retrieve a single record from the database."""

        result = await self._db_client[db_name][table].find_one(query)
        result = self._convert_object_id(result)

        return result

    async def update(self,
                     db_name: str,
                     table: str,
                     data: dict,
                     query: dict) -> tuple:
        """Update records in the database."""

        result = await self._db_client[db_name][table].update_many(query, {"$set": data})

        return result, result.matched_count

    async def delete(self,
                     db_name: str,
                     table: str,
                     query: dict) -> tuple:
        """Delete records from the database."""

        result = await self._db_client[db_name][table].delete_many(query)

        return result, result.deleted_count

    async def delete_one(self,
                         db_name: str,
                         table: str,
                         query: dict) -> tuple:
        """Delete records from the database."""

        result = await self._db_client[db_name][table].delete_one(query)

        return result, result.deleted_count

    async def get_next_sequence(self, db_name: str, sequence_name: str) -> int:
        """Return the next integer in a named atomic counter sequence.

        Uses MongoDB's findOneAndUpdate + $inc to guarantee that no two
        concurrent callers can ever receive the same value — eliminating the
        read-max-then-insert race condition.

        Counters are stored in the `counters` collection of `db_name`:
            { "_id": "<sequence_name>", "seq": <int> }

        The counter is created automatically on first use (upsert=True).
        The sequence is 1-based: the first call returns 1.
        """

        result = await self._db_client[db_name]["counters"].find_one_and_update(
            {"_id": sequence_name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        return int(result["seq"])

    async def sync_sequence(self, db_name: str, sequence_name: str, min_value: int) -> None:
        """Advance the named counter to at least min_value.

        Called whenever a manually-supplied key is accepted so that the next
        auto-generated key can never collide with any key the user has already
        inserted.

        Uses MongoDB's $max operator, which is a no-op when the stored seq is
        already >= min_value, and is itself atomic — safe under concurrency.

        Example: user inserts keys T1, T2, T4 manually.
            sync_sequence(..., 4) is called for each accepted key.
            Counter ends up at 4.  Next auto-generated key → T5.
        """

        await self._db_client[db_name]["counters"].update_one(
            {"_id": sequence_name},
            {"$max": {"seq": min_value}},
            upsert=True,
        )

    async def execute_raw(self,
                          command,
                          *args,
                          **kwargs):
        """ Execute a raw query or command
            (SQL for SQLite, command for MongoDB).
        """
