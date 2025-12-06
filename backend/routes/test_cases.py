# routes/test_cases.py

from typing import List

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


# Placeholder models (to be replaced with actual models from models/)
class TestCase(BaseModel):
    id: str
    short_name: str
    description: str


class TestCaseCreate(BaseModel):
    short_name: str
    description: str


class TestCaseUpdate(BaseModel):
    short_name: str
    description: str


class TestExecution(BaseModel):
    id: str
    result: str


class TestExecutionCreate(BaseModel):
    result: str


# List Test Cases
@router.get("/api/projects/{project_id}/test-cases/",
            tags=["test-cases"],
            response_model=List[TestCase])
def list_test_cases(project_id: str):
    return


# Create Test Case
@router.post("/api/projects/{project_id}/test-cases/",
             tags=["test-cases"],
             response_model=TestCase,
             status_code=status.HTTP_201_CREATED)
def create_test_case(project_id: str,
                     test_case: TestCaseCreate):
    return


# Get Test Case
@router.get("/api/projects/{project_id}/test-cases/{test_case_id}",
            tags=["test-cases"],
            response_model=TestCase)
def get_test_case(project_id: str,
                  test_case_id: str):
    return


# Update Test Case
@router.put("/api/projects/{project_id}/test-cases/{test_case_id}",
            tags=["test-cases"],
            response_model=TestCase)
def update_test_case(project_id: str,
                     test_case_id: str,
                     test_case: TestCaseUpdate):
    return


# Delete Test Case
@router.delete("/api/projects/{project_id}/test-cases/{test_case_id}",
               tags=["test-cases"],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(project_id: str,
                     test_case_id: str):
    return


# Get Test Case By Short Name
@router.get("/api/projects/{project_id}/test-cases/short-name/{short_name}",
            tags=["test-cases"],
            response_model=TestCase)
def get_test_case_by_short_name(project_id: str,
                                short_name: str):
    return