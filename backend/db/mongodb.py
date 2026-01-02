# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# db/mongodb.py

import logging
import os

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from backend.app_def.app_def import (
    DB_NAME,
    DB_COLLECTION_PRJ,
    DB_COLLECTION_TC,
    DB_COLLECTION_TE,
    DB_COLLECTION_TCY
)
from backend.db.db import (
    DatabaseClient,
    DBType,
    DBMode
)
from backend.models.projects import Project
from backend.models.test_cases import TestCase
from backend.models.test_cycles import TestCycle
from backend.models.test_executions import TestExecution


def pydantic_to_mongo_jsonschema(pydantic_schema: dict):
    """ Convert a Pydantic JSON schema to a MongoDB JSON schema,
        supporting Optionals (| None).
    """

    def is_required(field_name):
        """ Only non-optional fields should be required """

        field = pydantic_schema["properties"][field_name]
        if "anyOf" in field:
            for option in field["anyOf"]:
                if option.get("type") == "null":
                    return False

        if field.get("nullable"):
            return False

        return True

    type_map = {
        "string": "string",
        "integer": "int",
        "number": "double",
        "boolean": "bool"
    }

    props = {}
    required = pydantic_schema.get("required", [])
    for name, field in pydantic_schema["properties"].items():
        # Determine bsonType(s)
        bson_types = set()

        # Handle dict[str, str] (Pydantic v2: type == 'object' and 'properties' is empty and 'additionalProperties' is string)
        if field.get("type") == "object" and not field.get("properties") and field.get("additionalProperties", {}).get("type") == "string":
            props["_id" if name == "id" else name] = {
                "bsonType": "object",
                "additionalProperties": {"bsonType": "string"}
            }
            continue

        # Handle Pydantic's 'anyOf' for Optionals
        if "anyOf" in field:
            for option in field["anyOf"]:
                if option.get("type") == "null":
                    bson_types.add("null")

                elif option.get("type") == "array" and option.get("items", {}).get("type") == "string":
                    bson_types.add("array:string")

                elif option.get("type"):
                    bson_types.add(type_map.get(option["type"], option["type"]))

        else:
            # Handle 'nullable' (Pydantic 2+)
            if field.get("nullable"):
                bson_types.add("null")

            if field.get("type") == "array" and field.get("items", {}).get("type") == "string":
                bson_types.add("array:string")

            elif field.get("type"):
                bson_types.add(type_map.get(field["type"], field["type"]))

        # Convert array:string to MongoDB array of string
        if "array:string" in bson_types:
            bson_types.discard("array:string")
            arr_schema = {"bsonType": "array", "items": {"bsonType": "string"}}

            if bson_types:
                # e.g. array of string or null
                anyof_list = [arr_schema] + [{"bsonType": t} for t in bson_types if t != "null"]
                if "null" in bson_types:
                    anyof_list.append({"bsonType": "null"})

                arr_schema = {"anyOf": anyof_list}
                props["_id" if name == "id" else name] = arr_schema

            else:
                props["_id" if name == "id" else name] = arr_schema

        else:
            # If multiple types, use a list
            if len(bson_types) > 1:
                props["_id" if name == "id" else name] = {"bsonType": list(bson_types)}

            elif len(bson_types) == 1:
                props["_id" if name == "id" else name] = {"bsonType": list(bson_types)[0]}

            else:
                props["_id" if name == "id" else name] = {"bsonType": "string"}

    required_fields = ["_id" if r == "id" else r for r in required if is_required(r)]

    return {
        "bsonType": "object",
        "required": required_fields,
        "properties": props
    }


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

MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_USER = os.getenv("MONGODB_USER", "admin")
MONGODB_PASS = os.getenv("MONGODB_PASS", "password")

MONGODB_URL = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}"


class MongoClient(DatabaseClient):

    def __init__(self,
                 db_name: str = DB_NAME,
                 db_url: str = MONGODB_URL,
                 db_type: DBType = DBType.MONGODB,
                 db_mode: DBMode = DBMode.DEBUG):
        """ Initialize the MongoDB client. """

        super().__init__(db_name, db_url, db_type, db_mode)

    def _convert_objectid(self, doc: dict) -> dict:
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
        if self._db_mode == 'debug' or clean_db:
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
        results = [self._convert_objectid(p) for p in results]

        return results

    async def find_one(self,
                       table: str,
                       query: dict) -> dict:
        """Retrieve a single record from the database."""

        result = await self._db_client[self._db_name][table].find_one(query)
        result = self._convert_objectid(result)

        return result

    async def update(self,
                     table: str,
                     query: dict,
                     update_data: dict) -> tuple:
        """Update records in the database."""

        result = await self._db_client[self._db_name][table].update_many(query,
                                                                         {"$set": update_data})
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
