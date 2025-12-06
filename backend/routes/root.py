# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/root.py

import logging
from fastapi import APIRouter, Request
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


