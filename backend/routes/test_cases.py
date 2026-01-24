# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/test_cases.py

import json
import re

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app.app_def import (
    DB_COLLECTION_TC,
    TC_KEY_PREFIX,
    API_VERSION
)
from backend.app.utility import get_current_utc_time
from backend.models.test_cases import (
    TestCase,
    TestCaseCreate,
    TestCaseUpdate
)
from backend.routes.projects import get_project_by_key

router = APIRouter()


@router.get(f"/api/{API_VERSION}/tm/test-cases",
            tags=[DB_COLLECTION_TC],
            response_model=list[TestCase])
async def get_all_test_cases(request: Request):
    """Get all test cases."""

    # Retrieve all test cases from database
    db = request.app.state.mdb
    test_cases = await db.find(DB_COLLECTION_TC, {})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cases)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases",
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
    db = request.app.state.mdb
    test_cases = await db.find(DB_COLLECTION_TC,
                               {"project_key": project_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cases)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases",
             tags=[DB_COLLECTION_TC],
             status_code=status.HTTP_201_CREATED)
async def create_test_case_by_project(request: Request,
                                      project_key: str,
                                      test_case: TestCaseCreate):
    """Create a new test case in the specified project."""

    current_time = get_current_utc_time()

    # Prepare request data
    request_data = test_case.model_dump()

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Determine test_case_key
    test_case_key = request_data.get("test_case_key", None)

    if test_case_key is None:
        # Auto-generate test_case_key
        # get list of test cases in project to determine next key
        response = await get_all_test_cases_by_project(request, project_key)
        cases = json.loads(response.body.decode())
        if len(cases) < 1:
            # no test cases exist yet, start with 1
            last_tc = 1

        else:
            # extract numeric part of test_case_key to find last number
            key_n = [int(case["_id"].split(TC_KEY_PREFIX)[-1]) for case in cases]
            last_tc = max(key_n) + 1

        test_case_key = f"{project_key}-{TC_KEY_PREFIX}{last_tc}"
        request_data["test_case_key"] = test_case_key

    else:
        # Check if test_case_key already exists
        response = await get_test_case_by_key(request, project_key, test_case_key)
        if response.status_code != status.HTTP_404_NOT_FOUND:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"test case {test_case_key} already exists."})

        # regex check for valid test_case_key format
        # Must be PRJ_KEY-T###
        pattern = rf"^{project_key}-{TC_KEY_PREFIX}\d+$"
        if not re.match(pattern, test_case_key):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"test case key '{test_case_key}' is not valid. "
                                  f"Must be in format {project_key}-{TC_KEY_PREFIX}#"})

    # Initialize counts and timestamps
    request_data["project_key"] = project_key
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time

    # Assign _id
    db_insert = TestCase(**request_data).model_dump()
    db_insert["_id"] = test_case_key

    # Create the test case in the database
    db = request.app.state.mdb
    await db.create(DB_COLLECTION_TC, db_insert)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)



@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases",
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
    db = request.app.state.mdb
    await db.delete(DB_COLLECTION_TC,
                    {"project_key": project_key})

    # TODO: check test case count

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}",
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
    db = request.app.state.mdb
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


@router.put(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}",
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
    db = request.app.state.mdb
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


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}",
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
    db = request.app.state.mdb
    await db.delete_one(DB_COLLECTION_TC,
                        {"test_case_key": test_case_key,
                         "project_key": project_key})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
