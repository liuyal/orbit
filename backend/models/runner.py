# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# model/runner.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Runner(BaseModel):
    _id: int
    id: int
    name: str
    os: str
    status: str
    busy: bool
    labels: list
    queried_ts: int
    designation: str
    job: str
    job_url: str
    user: str
    model_config = {"extra": "forbid"}
