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

from backend.app.app_def import (
    API_VERSION
)
from backend.models.runner import Runner

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/api/{API_VERSION}/runners/status",
            tags=["runners"],
            status_code=status.HTTP_200_OK)
async def get_runners_status(request: Request):
    """ Get the status of all runners. """

    # Retrieve status from cache
    cache = getattr(request.app.state, "runner_status_cache", [])

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=cache)


@router.get(f"/api/{API_VERSION}/runners/status/{{name}}",
            tags=["runners"],
            response_model=Runner,
            status_code=status.HTTP_200_OK)
async def get_runners_status_by_name(request: Request,
                                     name: str):
    """ Get the status of a runners. """

    # Retrieve runner from database
    cache = getattr(request.app.state, "runner_status_cache", [])

    result = None
    for item in cache:
        if item["name"] == name:
            result = item
            break

    if result is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": f"Runner {name} not found"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=result)
