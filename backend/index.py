# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Version: 0.1.0
# Author: Jerry
# License: MIT
# ================================================================

import argparse
import logging.config
import os
import pathlib
from contextlib import asynccontextmanager

import uvicorn
import yaml
from fastapi import FastAPI

from db import (
    get_db_client,
    DB_NAME,
    DB_COLLECTIONS
)
from routes import routers

logger = logging.getLogger(__name__)


def build_parser():
    """ Build argument parser. """

    parser = argparse.ArgumentParser(
        description='Orbit FastAPI Backend'
    )
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='Set server to debug'
    )
    return parser


@asynccontextmanager
async def lifespan(app):
    """ Lifespan context manager to handle startup and shutdown events. """

    client = get_db_client()

    # Drop the database if in debug mode
    if args.debug:
        await client.drop_database(DB_NAME)

    # Initialize the database
    if DB_NAME not in await client.list_database_names():
        await client[DB_NAME].drop_collection("init")
        await client[DB_NAME].create_collection("init")

    # Initialize required collections
    collections = await client[DB_NAME].list_collection_names()
    for item in DB_COLLECTIONS:
        if item not in collections:
            await client[DB_NAME].create_collection(item)

    # Attach the database client to the app state
    app.state.db = client[DB_NAME]
    yield
    client.close()


def configure_logging_file(debug: bool = False) -> str:
    """ Configure logging from file. """

    tmp_path = os.getenv("TEMP", str(pathlib.Path(__file__).parent / 'tmp'))
    tmp_path = pathlib.Path(tmp_path)

    with open(pathlib.Path(__file__).parent / 'log_conf.yaml', 'r') as f:
        conf_text = f.read()
        if debug:
            conf_text = conf_text.replace('<LEVEL>', "DEBUG")

        else:
            conf_text = conf_text.replace('<LEVEL>', "INFO")

        log_conf_text = yaml.safe_load(conf_text)

    log_conf_path = tmp_path / 'log_conf.yaml'
    with open(log_conf_path, 'w') as f:
        yaml.dump(log_conf_text, f)

    return str(log_conf_path)


parser = build_parser()
args = parser.parse_args()

app = FastAPI(title="ORBIT",
              description="API spec for Orbit application",
              version="0.1.0",
              debug=args.debug,
              lifespan=lifespan)

for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    log_conf = configure_logging_file(args.debug)
    uvicorn.run("index:app",
                host="0.0.0.0",
                port=5080,
                reload=args.debug,
                log_config=log_conf)
