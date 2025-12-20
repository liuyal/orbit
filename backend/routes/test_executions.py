# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/execution.py

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app_def.app_def import (
    DB_COLLECTION_TE
)
from backend.models.test_executions import (
    TestExecution,
    TestExecutionCreate,
    TestExecutionUpdate
)
from backend.routes.projects import get_project_by_key
from backend.routes.test_cases import get_test_case_by_key

router = APIRouter()


@router.get("/tm/api/v1/projects/{project_key}/test-cases/{test_case_key}/executions",
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
    db = request.app.state.db
    test_executions = await db.find(DB_COLLECTION_TE,
                                    {"project_key": project_key,
                                     "test_case_key": test_case_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_executions)


@router.post("/tm/api/v1/projects/{project_key}/test-cases/{test_case_key}/executions",
             tags=[DB_COLLECTION_TE],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
async def create_execution_for_test_case(request: Request,
                                         project_key: str,
                                         test_case_key: str,
                                         execution: TestExecutionCreate):
    """Create a new test execution for a specific test case within a project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check if test_case_key exists
    response = await get_test_case_by_key(request, project_key, test_case_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data
    request_data = execution.model_dump()
    execution_key = request_data["execution_key"]

    # Validate execution_key starts with project_key
    if not execution_key.startswith(project_key):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"execution_key {execution_key} "
                              f"does not belong to project {project_key}"})

    # Check if execution_key already exists
    db = request.app.state.db
    result = await db.find_one(DB_COLLECTION_TE,
                               {"execution_key": execution_key})
    if result is not None:
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
    await db.create(DB_COLLECTION_TE, db_insert)

    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/tm/api/v1/projects/{project_key}/test-cases/{test_case_key}/executions",
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
    db = request.app.state.db
    result, deleted_count = await db.delete(DB_COLLECTION_TE,
                                            {"project_key": project_key,
                                             "test_case_key": test_case_key})
    if deleted_count == 0:
        # Test case has no executions
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": f"No test executions found "
                                              f"for test case {test_case_key}"})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tm/api/v1/executions/{execution_key}",
            tags=[DB_COLLECTION_TE],
            response_model=TestExecution)
async def get_execution(request: Request,
                        execution_key: str):
    """Retrieve a specific test execution by its ID."""

    # Retrieve test execution from database
    db = request.app.state.db
    test_execution = await db.find_one(DB_COLLECTION_TE,
                                       {"execution_key": execution_key})
    if test_execution is None:
        # test execution not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test execution {execution_key} not found"})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_execution)


@router.put("/tm/api/v1/executions/{execution_key}",
            tags=[DB_COLLECTION_TE],
            response_model=TestExecutionUpdate)
async def update_execution(request: Request,
                           execution_key: str,
                           execution: TestExecutionUpdate):
    """Update a specific test execution by its ID."""

    # Check execution exists
    response = await get_execution(request, execution_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data, excluding None values
    request_data = execution.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}

    # Update the execution in the database
    db = request.app.state.db
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


@router.delete("/tm/api/v1/executions/{execution_key}",
               tags=[DB_COLLECTION_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution(request: Request,
                           execution_key: str):
    """Delete a specific test execution by its ID."""

    # Delete the project from the database
    db = request.app.state.db
    result, deleted_count = await db.delete_one(
        DB_COLLECTION_TE,
        {"execution_key": execution_key})

    if deleted_count == 0:
        # Test execution not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test execution {execution_key} not found"})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
