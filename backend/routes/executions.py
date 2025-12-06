# routes/execution.py

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class TestExecution(BaseModel):
    id: str
    result: str
    status: str
    started_at: str
    finished_at: str
    logs: str


class TestExecutionUpdate(BaseModel):
    result: str


class TestExecutionCreate(BaseModel):
    result: str


class CycleExecutionLink(BaseModel):
    execution_id: str


# Get Execution
@router.get("/api/executions/{execution_id}",
            tags=["executions"],
            response_model=TestExecution)
def get_execution(execution_id: str):
    return


# Update Execution
@router.put("/api/executions/{execution_id}",
            tags=["executions"],
            response_model=TestExecution)
def update_execution(execution_id: str):
    return


# List Executions For Test Case
@router.get("/api/projects/{project_id}/test-cases/{test_case_id}/executions",
            tags=["executions"],
            response_model=list[TestExecution])
def list_executions_for_test_case(project_id: str,
                                  test_case_id: str):
    return


# Create Execution For Test Case
@router.post("/api/projects/{project_id}/test-cases/{test_case_id}/executions",
             tags=["executions"],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
def create_execution_for_test_case(project_id: str,
                                   test_case_id: str):
    return


# List Executions For Short Name
@router.get("/api/projects/{project_id}/test-cases/short-name/{short_name}/executions",
            tags=["executions"],
            response_model=list[TestExecution])
def list_executions_for_short_name(project_id: str,
                                   short_name: str):
    return


# Create Execution For Short Name
@router.post("/api/projects/{project_id}/test-cases/short-name/{short_name}/executions",
             tags=["executions"],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
def create_execution_for_short_name(project_id: str,
                                    short_name: str):
    return

