# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# model/execution.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TestExecution(BaseModel):
    _id: str
    execution_key: str
    project_key: str
    test_case_key: str
    test_cycle_key: str | None
    result: str | None
    custom_fields: dict | None
    comments: str | None
    started_at: str | None
    finished_at: str | None
    links: list[str] | None
    model_config = {"extra": "forbid"}


class TestExecutionCreate(BaseModel):
    execution_key: str = None
    test_case_key: str = None
    test_cycle_key: str = None
    result: str = None
    custom_fields: dict = None
    comments: str = None
    started_at: str = None
    finished_at: str = None
    links: list[str] = None
    model_config = {"extra": "forbid"}


class TestExecutionUpdate(BaseModel):
    result: str = None
    custom_fields: dict = None
    comments: str = None
    started_at: str = None
    finished_at: str = None
    links: list[str] = None
    model_config = {"extra": "forbid"}
