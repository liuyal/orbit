# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/root.py

import logging

from fastapi import APIRouter, Request, status, Response
from fastapi.responses import RedirectResponse

from backend.app.app_def import (
    API_VERSION,
    DB_ALL,
    DB_NAME_TM,
    DB_NAME_RUNNERS
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/", tags=["root"])
async def root(request: Request):
    """ Root endpoint to check service status. """

    logger.info(f"ROOT ENDPOINT")
    logger.debug("ROOT ENDPOINT DEBUG")

    # TODO add service status info
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}",
            tags=["root"])
async def root_api(request: Request):
    """ Root api endpoint to check service status. """

    logger.debug(f"/api/{API_VERSION} path redirecting to docs pages")
    base_url = f"{request.url.scheme}://{request.url.netloc}"

    return RedirectResponse(url=f"{base_url}/api/{API_VERSION}/docs")


@router.post(f"/api/{API_VERSION}/reset-database",
             tags=["root"],
             status_code=status.HTTP_204_NO_CONTENT)
async def reset_database(request: Request,
                         db_target: str = "ALL"):
    """ Root endpoint to reset server database. """

    db = request.app.state.mdb

    # Reset the database
    if db_target.upper().endswith("TM"):
        db_target = [DB_NAME_TM]

    elif db_target.upper().endswith("RUNNERS"):
        db_target = [DB_NAME_RUNNERS]

    else:
        db_target = DB_ALL

    await db.configure(clean_db=db_target)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
