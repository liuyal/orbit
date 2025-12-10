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

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/", tags=["root"])
async def root(request: Request):
    """ Root endpoint to check service status. """

    logger.info(f"root endpoint")
    logger.debug("root endpoint DEBUG")

    # TODO add service status info
    return RedirectResponse(url="/docs")


@router.post("/tm/api/v1/reset", tags=["root"])
async def reset_server(request: Request):
    """ Root endpoint to reset server. """

    db = request.app.state.db
    await db.configure(clean_db=True)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
