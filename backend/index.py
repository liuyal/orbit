# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import asyncio
import logging.config
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from backend.app.app_def import API_VERSION, ROOT_DIR
from backend.app.build_parser import build_parser
from backend.app.utility import configure_logging
from backend.db.mongodb import MongoClient
from backend.module.runners import save_runner_status
from backend.routes import routers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """ Lifespan context manager to handle startup
        and shutdown events.
    """

    # Initialize mongo client
    mongodb_client = MongoClient()
    await mongodb_client.connect()
    await mongodb_client.configure()

    # Start the background task to save runner status periodically
    runner_task = asyncio.create_task(save_runner_status(app, mongodb_client))
    logger.info("Started background task")

    # Attach the database client to the app state
    app.state.mdb = mongodb_client

    # Startup complete
    yield

    # Cleanup: Cancel the background task
    runner_task.cancel()
    try:
        await runner_task

    except asyncio.CancelledError:
        logger.info("Background task cancelled successfully")

    # Close the mongo client connection
    await mongodb_client.close()


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
    log_conf = configure_logging(ROOT_DIR / 'log_conf.yaml',
                                 args.debug)

    uvicorn.run("index:app",
                host=args.host,
                port=int(args.port),
                reload=args.debug,
                log_config=log_conf)
