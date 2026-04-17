# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/test_cases.py

import asyncio
import re
from typing import Optional

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from natsort import natsorted
from starlette.responses import JSONResponse

from backend.app.app_def import (
    API_VERSION,
    DB_COLLECTION_TM_PRJ,
    DB_COLLECTION_TM_TC,
    DB_COLLECTION_TM_TE,
    DB_NAME_TM,
    TC_KEY_PREFIX
)
from backend.app.utility import get_current_utc_time
from backend.models.test_cases import (
    TestCase,
    TestCaseCreate,
    TestCaseUpdate
)

router = APIRouter()

DB_NAME_TM = DB_NAME_TM.name
DB_COLLECTION_TM_PRJ = DB_COLLECTION_TM_PRJ.name
DB_COLLECTION_TM_TC = DB_COLLECTION_TM_TC.name
DB_COLLECTION_TM_TE = DB_COLLECTION_TM_TE.name


@router.get(f"/api/{API_VERSION}/tm/test-cases",
            tags=[DB_COLLECTION_TM_TC],
            response_model=list[TestCase],
            status_code=status.HTTP_200_OK)
async def get_all_test_cases(request: Request):
    """Get all test cases"""

    db = request.app.state.mdb

    # Retrieve all test cases from database
    test_cases = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TC, {})

    # Sort test cases by test_case_key using natsort
    test_cases = natsorted(test_cases, key=lambda x: x.get("test_case_key"))

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cases)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases",
            tags=[DB_COLLECTION_TM_TC],
            response_model=list[TestCase],
            status_code=status.HTTP_200_OK)
async def get_all_test_cases_by_project(request: Request,
                                        project_key: str):
    """Get all test cases in the specified project"""

    db = request.app.state.mdb

    # Concurrently check project exists and fetch test cases
    project, test_cases = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Sort test cases by test_case_key using natsort
    test_cases = natsorted(test_cases, key=lambda x: x.get("test_case_key"))

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cases)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-case",
             tags=[DB_COLLECTION_TM_TC],
             status_code=status.HTTP_201_CREATED)
async def create_test_case_in_project(request: Request,
                                      project_key: str,
                                      test_case: Optional[TestCaseCreate] = None):
    """Create a new test case in the specified project"""

    db = request.app.state.mdb

    # Check project exists
    project = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {
        "project_key": project_key
    })
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    if test_case:
        request_data = test_case.model_dump()
        test_case_key = request_data.get("test_case_key", None)

    else:
        request_data = TestCaseCreate().model_dump()
        test_case_key = None

    if test_case_key is None:
        # Auto-generate test_case_key — fetch only _id fields, no full documents
        existing_keys = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TC,
                                      {"project_key": project_key},
                                      {"_id": 1})
        if len(existing_keys) < 1:
            last_tc = 1

        else:
            last_tc = max([int(case["_id"].split(TC_KEY_PREFIX)[-1]) for case in existing_keys]) + 1

        test_case_key = f"{project_key}-{TC_KEY_PREFIX}{last_tc}"
        request_data["test_case_key"] = test_case_key

    else:
        # regex check for valid test_case_key format, must be PRJ_KEY-T#
        pattern = rf"^{project_key}-{TC_KEY_PREFIX}\d+$"
        if not re.match(pattern, test_case_key):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Key '{test_case_key}' is not valid. "
                                  f"Must be in format {project_key}-{TC_KEY_PREFIX}#"
                         }
            )

        # Check if test_case_key already exists with direct find_one
        existing = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {
            "test_case_key": test_case_key,
            "project_key": project_key
        })
        if existing is not None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"{test_case_key} already exists"}
            )

    # Initialize counts and timestamps
    current_time = get_current_utc_time()
    request_data["project_key"] = project_key
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time
    request_data["labels"] = [l.strip() for l in request_data.get("labels", [])]

    # Assign _id
    db_insert = TestCase(**request_data).model_dump()
    db_insert["_id"] = test_case_key

    # Create the test case in the database
    await db.create(DB_NAME_TM, DB_COLLECTION_TM_TC, db_insert)

    # Update project test case count using db.count + update labels
    tc_count = await db.count(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project_key})
    project["labels"] = list(set(project.get("labels", []) + request_data["labels"]))
    project["test_case_count"] = tc_count
    await db.update(DB_NAME_TM, DB_COLLECTION_TM_PRJ, project, {
        "project_key": project_key
    })

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases",
               tags=[DB_COLLECTION_TM_TC],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_test_case_from_project(request: Request,
                                            project_key: str):
    """Delete all test cases in the specified project"""

    db = request.app.state.mdb

    # Concurrently check project exists and check for linked executions
    project, execution_count = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.count(DB_NAME_TM, DB_COLLECTION_TM_TE, {"project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    if execution_count > 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Test cases in project {project_key} have "
                              f"linked test executions and cannot be deleted"}
        )

    # Delete all test cases under project
    await db.delete(DB_NAME_TM, DB_COLLECTION_TM_TC, {
        "project_key": project_key
    })

    # Update project test counts to 0 using already-fetched project doc
    project["test_case_count"] = 0
    project["test_cycle_count"] = 0

    await db.update(DB_NAME_TM, DB_COLLECTION_TM_PRJ, project, {
        "project_key": project_key
    })

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}",
            tags=[DB_COLLECTION_TM_TC],
            response_model=TestCase)
async def get_test_case_by_key(request: Request,
                               project_key: str,
                               test_case_key: str):
    """Retrieve a specific test case by its ID within the specified project"""

    db = request.app.state.mdb

    # Concurrently check project exists and fetch test case
    project, result = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {"test_case_key": test_case_key,
                                                      "project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=result)


@router.put(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}",
            tags=[DB_COLLECTION_TM_TC],
            response_model=TestCase)
async def update_test_case_by_key(request: Request,
                                  project_key: str,
                                  test_case_key: str,
                                  test_case: TestCaseUpdate):
    """Update a specific test case by its ID within the specified project"""

    db = request.app.state.mdb

    # Concurrently check project and test case exist
    project, existing_tc = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {"test_case_key": test_case_key,
                                                      "project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    if existing_tc is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    # Prepare request data, excluding None values
    request_data = test_case.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["labels"] = [l.strip() for l in request_data.get("labels", [])]
    request_data["updated_at"] = get_current_utc_time()

    # Update the test case in the database
    await db.update(DB_NAME_TM, DB_COLLECTION_TM_TC, request_data, {
        "project_key": project_key,
        "test_case_key": test_case_key,
    })

    # Retrieve the updated test case
    updated_test_case = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {
        "test_case_key": test_case_key,
        "project_key": project_key
    })

    # Update project labels if changed
    new_label_set = list(set(project.get("labels", []) + request_data["labels"]))
    if project["labels"] != new_label_set:
        project["labels"] = new_label_set
        await db.update(DB_NAME_TM, DB_COLLECTION_TM_PRJ, project, {
            "project_key": project_key
        })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_test_case)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}",
               tags=[DB_COLLECTION_TM_TC],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case_by_key(request: Request,
                                  project_key: str,
                                  test_case_key: str):
    """Delete a specific test case by its ID within the specified project"""

    db = request.app.state.mdb

    # Concurrently check project, test case, and execution count
    project, existing_tc, execution_count = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {"test_case_key": test_case_key,
                                                      "project_key": project_key}),
        db.count(DB_NAME_TM, DB_COLLECTION_TM_TE, {"project_key": project_key,
                                                   "test_case_key": test_case_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    if existing_tc is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    if execution_count > 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Test case {test_case_key} has "
                              f"associated test executions and cannot be deleted"}
        )

    # Delete the test case and get updated count concurrently
    await db.delete_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {
        "test_case_key": test_case_key,
        "project_key": project_key
    })

    # Update project test case count using db.count
    project["test_case_count"] = await db.count(DB_NAME_TM, DB_COLLECTION_TM_TC, {
        "project_key": project_key
    })
    await db.update(DB_NAME_TM, DB_COLLECTION_TM_PRJ, project, {
        "project_key": project_key
    })

    return Response(status_code=status.HTTP_204_NO_CONTENT)
