# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

from backend.app_def.build_parser import build_parser

parser = build_parser()
args = parser.parse_args()

import threading
import logging.config
import pathlib
from contextlib import asynccontextmanager

import uvicorn
import yaml
from fastapi import FastAPI

from backend.db.mongodb import MongoClient
from backend.routes import routers
from backend.app_def.app_def import API_VERSION#, RUNNERS_DB_FILE
# from backend.module.runners import query_runner_status

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """ Lifespan context manager to handle startup and shutdown events. """

    # Initialize mongo client
    mongodb_client = MongoClient()
    await mongodb_client.connect()
    await mongodb_client.configure()

    # Start the runner status query thread
    kill = threading.Event()
    # thread_runner = threading.Thread(target=query_runner_status,
    #                                  args=(kill, pathlib.Path(args.output) / f"{RUNNERS_DB_FILE}"),
    #                                  name="RUNNER_THREAD",
    #                                  daemon=True)
    # thread_runner.start()

    # Attach the database client to the app state
    app.state.mdb = mongodb_client
    yield
    await mongodb_client.close()
    # thread_runner.join(1)


def configure_logging_file(debug: bool = False) -> str:
    """ Configure logging from file. """

    tmp_path = pathlib.Path(__file__).parent / 'tmp'
    tmp_path.mkdir(parents=True, exist_ok=True)

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
    log_conf = configure_logging_file(args.debug)
    uvicorn.run("index:app",
                host=args.host,
                port=int(args.port),
                reload=args.debug,
                log_config=log_conf)
