# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging.config
import os
import pathlib
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from backend.app.app_def import API_VERSION
from backend.db.mongodb import MongoClient
from backend.db.sqlite import SqliteClient
from backend.module.runners import query_runner_status
from backend.routes import routers
from backend.app.build_parser import build_parser
from backend.app.utility import configure_logging_file

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """ Lifespan context manager to handle startup and shutdown events. """

    query_runner_status(pathlib.Path(os.getenv("SQLITE_DATABASE")))

    # Initialize sqlite client
    sqlite_client = SqliteClient()
    await sqlite_client.connect()
    await sqlite_client.configure()

    # Initialize mongo client
    mongodb_client = MongoClient()
    await mongodb_client.connect()
    await mongodb_client.configure()

    # Attach the database client to the app state
    app.state.mdb = mongodb_client
    app.state.sqdb = sqlite_client
    yield
    await mongodb_client.close()
    await sqlite_client.close()


parser = build_parser()
args = parser.parse_args()

app = FastAPI(title="ORBIT",
              description="API spec for Orbit application",
              version="0.1.0",
              docs_url=f"/api/{API_VERSION}/docs",
              redoc_url=f"/api/{API_VERSION}/redoc",
              openapi_url=f"/api/{API_VERSION}/openapi.json",
              debug=args.debug,
              lifespan=lifespan)

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    log_conf = configure_logging_file(pathlib.Path(__file__).parent / 'log_conf.yaml',
                                      args.debug)
    uvicorn.run("index:app",
                host=args.host,
                port=int(args.port),
                reload=args.debug,
                log_config=log_conf)
