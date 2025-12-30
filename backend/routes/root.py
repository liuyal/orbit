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

from backend.app_def.app_def import API_VERSION

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/", tags=["root"])
async def root(request: Request):
    """ Root endpoint to check service status. """

    logger.info(f"root endpoint")
    logger.debug("root endpoint DEBUG")

    # TODO add service status info
    return RedirectResponse(url=f"/api/{API_VERSION}/docs")


@router.get(f"/api/{API_VERSION}", tags=["root"])
async def root_api(request: Request):
    """ Root api endpoint to check service status. """

    # TODO add service status info
    return RedirectResponse(url=f"/api/{API_VERSION}/docs")


@router.post(f"/api/{API_VERSION}/tm/reset", tags=["root"])
async def reset_tm_server(request: Request):
    """ Root endpoint to reset server. """

    db = request.app.state.db
    await db.configure(clean_db=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
