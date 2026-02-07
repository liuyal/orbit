# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# model/cycles.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TestCycle(BaseModel):
    _id: str
    test_cycle_key: str
    project_key: str
    title: str | None
    description: str | None
    created_at: str | None
    updated_at: str | None
    status: str | None
    executions: dict = {}
    model_config = {"extra": "forbid"}


class TestCycleCreate(BaseModel):
    test_cycle_key: str = None
    title: str = None
    description: str = None
    status: str = None
    executions: dict = {}
    model_config = {"extra": "forbid"}


class TestCycleUpdate(BaseModel):
    title: str = None
    description: str = None
    status: str = None
    executions: dict = {}
    model_config = {"extra": "forbid"}
