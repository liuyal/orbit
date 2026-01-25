# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/runner.py

import logging

from fastapi import APIRouter, Request, status
from starlette.responses import JSONResponse

from backend.app.app_def import API_VERSION

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/api/{API_VERSION}/runners/status",
            tags=["runners"],
            status_code=status.HTTP_200_OK)
async def get_runners_status(request: Request):
    """ Get the status of all runners. """

    runners_stats = {}

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=runners_stats)
