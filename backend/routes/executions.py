# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/execution.py

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class TestExecution(BaseModel):
    id: str
    execution_key: str
    project_key: str
    test_cycle_key: str
    test_case_key: str
    result: str
    custom_fields: dict[str, str]
    comments: str
    started_at: str
    finished_at: str
    links: list[str]


class TestExecutionCreate(BaseModel):
    execution_key: str
    project_key: str
    test_cycle_key: str
    test_case_key: str
    result: str = None
    custom_fields: dict[str, str] = None
    comments: str = None
    started_at: str = None
    finished_at: str = None
    links: list[str] = None


class TestExecutionUpdate(BaseModel):
    execution_key: str
    result: str = None
    custom_fields: dict[str, str] = None
    comments: str = None
    started_at: str = None
    finished_at: str = None
    links: list[str] = None


@router.get("/api/projects/{project_key}/test-cases/{test_case_key}/executions",
            tags=["executions"],
            response_model=list[TestExecution])
def list_executions_for_test_case(project_key: str,
                                  test_case_key: str):
    """List all test executions for a specific test case within a project."""


@router.post("/api/projects/{project_key}/test-cases/{test_case_key}/executions",
             tags=["executions"],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
def create_execution_for_test_case(project_key: str,
                                   test_case_key: str,
                                   execution: TestExecutionCreate):
    """Create a new test execution for a specific test case within a project."""


@router.get("/api/executions/{execution_key}",
            tags=["executions"],
            response_model=TestExecution)
def get_execution(execution_key: str):
    """Retrieve a specific test execution by its ID."""


@router.put("/api/executions/{execution_key}",
            tags=["executions"],
            response_model=TestExecutionUpdate)
def update_execution(execution_key: str,
                     execution: TestExecutionUpdate):
    """Update a specific test execution by its ID."""


@router.delete("/api/executions/{execution_key}",
               tags=["executions"],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_execution(execution_key: str):
    """Delete a specific test execution by its ID."""
