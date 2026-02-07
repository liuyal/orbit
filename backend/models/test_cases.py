# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/test_cases.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TestCase(BaseModel):
    _id: str
    test_case_key: str
    project_key: str
    title: str | None
    description: str | None
    folder: str | None
    created_at: str
    updated_at: str | None
    status: str | None
    priority: str | None
    test_script: str | None
    test_script_type: str | None
    last_result: str | None
    last_execution_key: str | None
    test_frequency: list = []
    labels: list = []
    links: list = []


class TestCaseCreate(BaseModel):
    test_case_key: str = None
    project_key: str = None
    title: str = None
    description: str = None
    folder: str = None
    status: str = None
    priority: str = None
    test_script: str = None
    test_script_type: str = None
    last_result: str = None
    last_execution_key: str = None
    test_frequency: list = []
    labels: list = []
    links: list = []


class TestCaseUpdate(BaseModel):
    title: str = None
    description: str = None
    folder: str = None
    status: str = None
    priority: str = None
    test_script: str = None
    test_script_type: str = None
    last_result: str = None
    last_execution_key: str = None
    test_frequency: list = []
    labels: list = []
    links: list = []
