# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/test_cases.py

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app_def.app_def import (
    DB_COLLECTION_TC
)
from backend.models.test_cases import (
    TestCase,
    TestCaseCreate,
    TestCaseUpdate
)
from backend.routes.projects import get_project_by_key
from backend.tools.tools import get_current_utc_time

router = APIRouter()


@router.get("/tm/api/v1/test-cases",
            tags=[DB_COLLECTION_TC],
            response_model=list[TestCase])
async def get_all_test_cases(request: Request):
    """Get all test cases."""

    # Retrieve all test cases from database
    db = request.app.state.db
    test_cases = await db.find(DB_COLLECTION_TC, {})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cases)


@router.get("/tm/api/v1/projects/{project_key}/test-cases",
            tags=[DB_COLLECTION_TC],
            response_model=list[TestCase])
async def get_all_test_cases_by_project(request: Request,
                                        project_key: str):
    """Get all test cases in the specified project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Retrieve test cases from database matching project_key
    db = request.app.state.db
    test_cases = await db.find(DB_COLLECTION_TC,
                               {"project_key": project_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cases)


@router.post("/tm/api/v1/projects/{project_key}/test-cases",
             tags=[DB_COLLECTION_TC],
             status_code=status.HTTP_201_CREATED)
async def create_test_case_by_project(request: Request,
                                      project_key: str,
                                      test_case: TestCaseCreate):
    """Create a new test case in the specified project."""

    current_time = get_current_utc_time()

    # Prepare request data
    request_data = test_case.model_dump()
    test_case_key = request_data["test_case_key"]

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check if test_case_key already exists
    response = await get_test_case_by_key(request, project_key, test_case_key)
    if response.status_code != status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"test case {test_case_key} already exists."})

    # Validate that test_case starts with project_key
    if not request_data["test_case_key"].startswith(project_key):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Test case {test_case_key} "
                              f"does not belong to project {project_key}"})

    # Initialize counts and timestamps
    request_data["project_key"] = project_key
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time

    # Assign _id
    db_insert = TestCase(**request_data).model_dump()
    db_insert["_id"] = test_case_key

    # Create the test case in the database
    db = request.app.state.db
    await db.create(DB_COLLECTION_TC, db_insert)

    return Response(status_code=status.HTTP_201_CREATED)


@router.delete("/tm/api/v1/projects/{project_key}/test-cases",
               tags=[DB_COLLECTION_TC],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_test_case_by_project(request: Request,
                                          project_key: str):
    """Delete all test cases in the specified project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # TODO: Check if test case is linked to any test executions

    # Delete test cases from database matching project_key
    db = request.app.state.db
    await db.delete(DB_COLLECTION_TC,
                    {"project_key": project_key})

    # TODO: check test case count

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/tm/api/v1/projects/{project_key}/test-cases/{test_case_key}",
            tags=[DB_COLLECTION_TC],
            response_model=TestCase)
async def get_test_case_by_key(request: Request,
                               project_key: str,
                               test_case_key: str):
    """Retrieve a specific test case by its ID within the specified project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Retrieve test case from database
    db = request.app.state.db
    result = await db.find_one(DB_COLLECTION_TC,
                               {"test_case_key": test_case_key,
                                "project_key": project_key})
    if result is None:
        # test case not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test case {test_case_key} not found"})
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result)


@router.put("/tm/api/v1/projects/{project_key}/test-cases/{test_case_key}",
            tags=[DB_COLLECTION_TC],
            response_model=TestCase)
async def update_test_case_by_key(request: Request,
                                  project_key: str,
                                  test_case_key: str,
                                  test_case: TestCaseUpdate):
    """Update a specific test case by its ID within the specified project."""

    current_time = get_current_utc_time()

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check if test_case_key exists
    response = await get_test_case_by_key(request, project_key, test_case_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data, excluding None values
    request_data = test_case.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["updated_at"] = current_time

    # Update the project in the database
    db = request.app.state.db
    await db.update(DB_COLLECTION_TC,
                    {"test_case_key": test_case_key,
                     "project_key": project_key},
                    request_data)

    # Retrieve the updated test case
    updated_test_case = await db.find_one(DB_COLLECTION_TC,
                                          {"test_case_key": test_case_key,
                                           "project_key": project_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_test_case)


@router.delete("/tm/api/v1/projects/{project_key}/test-cases/{test_case_key}",
               tags=[DB_COLLECTION_TC],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case_by_key(request: Request,
                                  project_key: str,
                                  test_case_key: str):
    """Delete a specific test case by its ID within the specified project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check if test_case_key exists
    response = await get_test_case_by_key(request, project_key, test_case_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # TODO: Check if test case is linked to any test executions

    # Delete the test case from project from the database
    db = request.app.state.db
    await db.delete_one(DB_COLLECTION_TC,
                        {"test_case_key": test_case_key,
                         "project_key": project_key})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
