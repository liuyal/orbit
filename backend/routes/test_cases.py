# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/test_cases.py

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class TestCase(BaseModel):
    id: str
    test_case_key: str
    project_key: str
    title: str
    description: str
    folder: str
    status: str
    priority: str
    test_scripts: str = None
    last_result: str = None
    last_execution_id: str = None
    test_frequency: list[str] = None
    labels: list[str] = None
    links: list[str] = None


class TestCaseCreate(BaseModel):
    test_case_key: str
    project_key: str
    title: str
    description: str
    folder: str
    status: str
    priority: str = None
    test_scripts: str = None
    last_result: str = None
    last_execution_key: str = None
    test_frequency: list[str] = None
    labels: list[str] = None
    links: list[str] = None


class TestCaseUpdate(BaseModel):
    title: str = None
    description: str = None
    folder: str = None
    status: str = None
    priority: str = None
    test_scripts: str = None
    last_result: str = None
    last_execution_key: str = None
    test_frequency: list[str] = None
    labels: list[str] = None
    links: list[str] = None


@router.get("/api/projects/{project_key}/test-cases/",
            tags=["test-cases"],
            response_model=list[TestCase])
def list_test_cases(project_key: str):
    """List all test cases in the specified project."""


@router.post("/api/projects/{project_key}/test-cases/",
             tags=["test-cases"],
             status_code=status.HTTP_204_NO_CONTENT)
def create_test_case(project_key: str,
                     test_case: TestCaseCreate):
    """Create a new test case in the specified project."""


@router.delete("/api/projects/{project_key}/test-cases/",
               tags=["test-cases"],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_all_test_case(project_key: str):
    """Delete all test cases in the specified project."""


@router.get("/api/projects/{project_key}/test-cases/{test_case_key}",
            tags=["test-cases"],
            response_model=TestCase)
def get_test_case_by_key(project_key: str,
                         test_case_key: str):
    """Retrieve a specific test case by its ID within the specified project."""


@router.put("/api/projects/{project_key}/test-cases/{test_case_key}",
            tags=["test-cases"],
            response_model=TestCase)
def update_test_case_by_key(project_key: str,
                            test_case_key: str,
                            test_case: TestCaseUpdate):
    """Update a specific test case by its ID within the specified project."""


@router.delete("/api/projects/{project_key}/test-cases/{test_case_key}",
               tags=["test-cases"],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case_by_key(project_key: str,
                            test_case_key: str):
    """Delete a specific test case by its ID within the specified project."""
