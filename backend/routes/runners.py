# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/runner.py

import logging

from fastapi import APIRouter, Request, status, Response

from backend.app_def.app_def import API_VERSION

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/api/{API_VERSION}/runners/status", tags=["runners"])
async def get_runners_status(request: Request):
    """ Get the status of all runners. """


    return Response(status_code=status.HTTP_204_NO_CONTENT)
