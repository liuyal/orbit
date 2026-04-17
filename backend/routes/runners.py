# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/runner.py

import logging

from fastapi import (
    APIRouter,
    Request,
    status
)
from starlette.responses import JSONResponse

from backend.app.app_def import (
    API_VERSION,
    RUNNER_STATUS_CACHE
)
from backend.models.runner import Runner

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/api/{API_VERSION}/runners/status",
            tags=["runners"],
            response_model=Runner,
            status_code=status.HTTP_200_OK)
async def get_runners_status(request: Request):
    """ Get the status of all runners. """

    # Retrieve status from cache (dict keyed by name), return as list
    cache = getattr(request.app.state, RUNNER_STATUS_CACHE, {})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=list(cache.values()))


@router.get(f"/api/{API_VERSION}/runners/status/{{name}}",
            tags=["runners"],
            response_model=Runner,
            status_code=status.HTTP_200_OK)
async def get_runners_status_by_name(request: Request,
                                     name: str):
    """ Get the status of a runner. """

    # Retrieve runner from cache via dict lookup
    cache = getattr(request.app.state, RUNNER_STATUS_CACHE, {})
    runner = cache.get(name)

    if runner is None:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": f"{name} not found"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=runner)

