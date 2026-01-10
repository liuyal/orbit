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
from backend.module.runners import (
    TABLE_RUNNER_STATS_CURRENT
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(f"/api/{API_VERSION}/runners/status",
            tags=["runners"],
            status_code=status.HTTP_200_OK)
async def get_runners_status(request: Request):
    """ Get the status of all runners. """

    db_conn = request.state.sqdb

    cursor = db_conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_RUNNER_STATS_CURRENT};")
    runners_stats = cursor.fetchall()

    return Response(status_code=status.HTTP_200_OK,
                    content=runners_stats)
