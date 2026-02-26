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

from backend.app.app_def import API_VERSION, TM_DB_COLLECTIONS

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/", tags=["root"])
async def root(request: Request):
    """ Root endpoint to check service status. """

    logger.info(f"root endpoint")
    logger.debug("root endpoint DEBUG")

    # TODO add service status info
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}",
            tags=["root"])
async def root_api(request: Request):
    """ Root api endpoint to check service status. """

    logger.debug(f"/api/{API_VERSION} path redirecting to docs pages")
    base_url = f"{request.url.scheme}://{request.url.netloc}"

    return RedirectResponse(url=f"{base_url}/api/{API_VERSION}/docs")


@router.post(f"/api/{API_VERSION}/reset",
             tags=["root"],
             status_code=status.HTTP_204_NO_CONTENT)
async def reset_server_db(request: Request):
    """ Root endpoint to reset server db. """

    # Reset the database
    db = request.app.state.mdb
    await db.configure(clean_db="all")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(f"/api/{API_VERSION}/tm/reset",
             tags=["root"],
             status_code=status.HTTP_204_NO_CONTENT)
async def reset_tm_server_db(request: Request):
    """ Root endpoint to reset tm server. """

    # Reset the database
    db = request.app.state.mdb
    await db.configure(clean_db="tm")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
