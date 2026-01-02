# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/execution.py

import json
import re

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app_def.app_def import (
    DB_COLLECTION_TE,
    TE_KEY_PREFIX,
    API_VERSION
)
from backend.models.test_executions import (
    TestExecution,
    TestExecutionCreate,
    TestExecutionUpdate
)
from backend.routes.projects import get_project_by_key
from backend.routes.test_cases import get_test_case_by_key

router = APIRouter()


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
            tags=[DB_COLLECTION_TE],
            response_model=list[TestExecution])
async def get_all_executions_for_test_case(request: Request,
                                           project_key: str,
                                           test_case_key: str):
    """Get all test executions for a specific test case within a project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check if test_case_key exists
    response = await get_test_case_by_key(request, project_key, test_case_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Retrieve test execution matching project_key and test_case_key
    db = request.app.state.mdb
    test_executions = await db.find(DB_COLLECTION_TE,
                                    {"project_key": project_key,
                                     "test_case_key": test_case_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_executions)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
             tags=[DB_COLLECTION_TE],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
async def create_execution_for_test_case(request: Request,
                                         project_key: str,
                                         test_case_key: str,
                                         execution: TestExecutionCreate):
    """Create a new test execution for a specific test case within a project."""

    # Prepare request data
    request_data = execution.model_dump()

    # Determine test_case_key
    execution_key = request_data.get("execution_key", None)

    if execution_key is None:
        # Auto-generate execution_key
        # get list of test execution to determine next key
        response = await get_all_executions_for_test_case(request,
                                                          project_key,
                                                          test_case_key)
        execution = json.loads(response.body.decode())
        if len(execution) < 1:
            # no test execution exist yet, start with 1
            last_te = 1

        else:
            # extract numeric part of test_case_key to find last number
            key_n = [int(e["_id"].split(TE_KEY_PREFIX)[-1]) for e in execution]
            last_te = max(key_n) + 1

        execution_key = f"{project_key}-{TE_KEY_PREFIX}{last_te}"
        request_data["execution_key"] = execution_key

    else:
        # Check project exists
        response = await get_project_by_key(request, project_key)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return response

        # Check if test_case_key exists
        response = await get_test_case_by_key(request, project_key, test_case_key)
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return response

        # regex check for valid execution_key format
        # Must be PRJ_KEY-E###
        pattern = rf"^{project_key}-{TE_KEY_PREFIX}\d+$"
        if not re.match(pattern, execution_key):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"test execution key '{execution_key}' is not valid. "
                                  f"Must be in format {project_key}-{TE_KEY_PREFIX}#"})

        # Check if execution_key already exists
        response = await get_execution_by_key(request, execution_key)
        if response.status_code != status.HTTP_404_NOT_FOUND:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"execution_key {execution_key} "
                                  f"already exists."})

    # Initialize missing keys
    request_data["project_key"] = project_key
    request_data["test_case_key"] = test_case_key

    # Assign _id
    db_insert = TestExecution(**request_data).model_dump()
    db_insert["_id"] = execution_key

    # Create the test execution in the database
    db = request.app.state.mdb
    await db.create(DB_COLLECTION_TE, db_insert)

    return Response(status_code=status.HTTP_201_CREATED)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
               tags=[DB_COLLECTION_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_execution_for_test_case(request: Request,
                                             project_key: str,
                                             test_case_key: str):
    """Delete all test executions for a specific test case within a project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check if test_case_key exists
    response = await get_test_case_by_key(request, project_key, test_case_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # delete all test executions for the specified test case
    db = request.app.state.mdb
    result, deleted_count = await db.delete(DB_COLLECTION_TE,
                                            {"project_key": project_key,
                                             "test_case_key": test_case_key})
    if deleted_count == 0:
        # Test case has no executions
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": f"No test executions found "
                                              f"for test case {test_case_key}"})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/executions/{{execution_key}}",
            tags=[DB_COLLECTION_TE],
            response_model=TestExecution)
async def get_execution_by_key(request: Request,
                               execution_key: str):
    """Retrieve a specific test execution by its ID."""

    # Retrieve test execution from database
    db = request.app.state.mdb
    test_execution = await db.find_one(DB_COLLECTION_TE,
                                       {"execution_key": execution_key})
    if test_execution is None:
        # test execution not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test execution {execution_key} not found"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_execution)


@router.put(f"/api/{API_VERSION}/tm/executions/{{execution_key}}",
            tags=[DB_COLLECTION_TE],
            response_model=TestExecutionUpdate)
async def update_execution_by_key(request: Request,
                                  execution_key: str,
                                  execution: TestExecutionUpdate):
    """Update a specific test execution by its ID."""

    # Check execution exists
    response = await get_execution_by_key(request, execution_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data, excluding None values
    request_data = execution.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}

    # Update the execution in the database
    db = request.app.state.mdb
    result, matched_count = await db.update(
        DB_COLLECTION_TE,
        {"execution_key": execution_key},
        request_data)

    if matched_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test execution {execution_key} not found"})

    # Retrieve the updated test case
    updated_test_execution = await db.find_one(
        DB_COLLECTION_TE,
        {"execution_key": execution_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_test_execution)


@router.delete(f"/api/{API_VERSION}/tm/executions/{{execution_key}}",
               tags=[DB_COLLECTION_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution_by_key(request: Request,
                                  execution_key: str):
    """Delete a specific test execution by its ID."""

    # Delete the project from the database
    db = request.app.state.mdb
    result, deleted_count = await db.delete_one(
        DB_COLLECTION_TE,
        {"execution_key": execution_key})

    if deleted_count == 0:
        # Test execution not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test execution {execution_key} not found"})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
