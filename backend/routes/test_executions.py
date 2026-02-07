# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/execution.py

import json
import re
from typing import Optional

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app.app_def import (
    DB_COLLECTION_PRJ,
    DB_COLLECTION_TE,
    DB_COLLECTION_TC,
    DB_COLLECTION_TCY,
    TE_KEY_PREFIX,
    API_VERSION
)
from backend.app.utility import get_current_utc_time
from backend.models.test_executions import (
    TestExecution,
    TestExecutionCreate,
    TestExecutionUpdate
)

router = APIRouter()


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/executions",
            tags=[DB_COLLECTION_TE],
            response_model=list[TestExecution],
            status_code=status.HTTP_200_OK)
async def get_all_executions_by_project(request: Request,
                                        project_key: str):
    """Get all test executions for a specific test case within a project"""

    db = request.app.state.mdb

    # Check project exists
    project = await db.find_one(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Retrieve test execution matching project_key
    test_executions = await db.find(DB_COLLECTION_TE, {
        "project_key": project_key
    })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_executions)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/executions",
               tags=[DB_COLLECTION_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_test_execution_by_project(request: Request,
                                               project_key: str):
    """Delete all test executions in the specified project"""

    db = request.app.state.mdb

    # Check project exists
    project = await db.find_one(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Set last_execution_key to None for all test cases in the project
    test_cases = await db.find(DB_COLLECTION_TC, {
        "project_key": project_key
    })
    for tc_data in test_cases:
        tc_data["updated_at"] = get_current_utc_time()
        tc_data["last_execution_key"] = None
        await db.update(DB_COLLECTION_TC, tc_data, {
            "project_key": project_key,
            "test_case_key": tc_data["test_case_key"]
        })

    # Set all execution_key to empty for all cycles in the project
    cycles = await db.find(DB_COLLECTION_TCY, {
        "project_key": project_key
    })
    for cycle in cycles:
        cycle["executions"] = {}
        cycle["updated_at"] = get_current_utc_time()
        await db.update(DB_COLLECTION_TCY, cycle, {
            "test_cycle_key": cycle["test_cycle_key"]
        })

    # Delete test executions from database matching project_key
    await db.delete(DB_COLLECTION_TE, {
        "project_key": project_key
    })

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
            tags=[DB_COLLECTION_TE],
            response_model=list[TestExecution],
            status_code=status.HTTP_200_OK)
async def get_all_executions_by_test_case_key(request: Request,
                                              project_key: str,
                                              test_case_key: str):
    """Get all test executions for a specific test case within a project"""

    db = request.app.state.mdb

    # Check project exists
    project = await db.find_one(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Check if test_case_key exists
    tc_data = await db.find_one(DB_COLLECTION_TC, {
        "test_case_key": test_case_key,
        "project_key": project_key
    })
    if tc_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    # Retrieve test execution matching project_key and test_case_key
    test_executions = await db.find(DB_COLLECTION_TE, {
        "project_key": project_key,
        "test_case_key": test_case_key
    })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_executions)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
             tags=[DB_COLLECTION_TE],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
async def create_execution_by_test_case_key(request: Request,
                                            project_key: str,
                                            test_case_key: str,
                                            execution: Optional[TestExecutionCreate] = None):
    """Create a new test execution for a specific test case within a project"""

    db = request.app.state.mdb

    # Check project exists
    project = await db.find_one(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Check if test_case_key exists
    tc_data = await db.find_one(DB_COLLECTION_TC, {
        "test_case_key": test_case_key,
        "project_key": project_key
    })
    if tc_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    if execution:
        # Prepare request data from request data
        request_data = execution.model_dump()
        execution_key = request_data.get("execution_key", None)

    else:
        # Prepare request data with default values
        request_data = TestExecutionCreate().model_dump()
        execution_key = None

    if execution_key is None:
        # Auto-generate execution_key
        # get list of test execution to determine next key
        response = await get_all_executions_by_project(request, project_key)
        execution = json.loads(response.body.decode())
        if len(execution) < 1:
            # no test execution exist yet, start with 1
            last_te = 1

        else:
            # extract numeric part of test_case_key to find last number
            key_n = [int(e["_id"].split(TE_KEY_PREFIX)[-1]) for e in execution]
            last_te = max(key_n) + 1

        # generate execution_key
        execution_key = f"{project_key}-{TE_KEY_PREFIX}{last_te}"
        request_data["execution_key"] = execution_key

    else:
        # regex check for valid execution_key format, must be PRJ_KEY-E#
        pattern = rf"^{project_key}-{TE_KEY_PREFIX}\d+$"
        if not re.match(pattern, execution_key):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"test execution key '{execution_key}' is not valid. "
                                  f"Must be in format {project_key}-{TE_KEY_PREFIX}#"}
            )

        # Check if execution_key already exists
        response = await get_execution_by_key(request, execution_key)
        if response.status_code != status.HTTP_404_NOT_FOUND:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"{execution_key} already exists"}
            )

    # Initialize missing keys
    current_time = get_current_utc_time()
    request_data["project_key"] = project_key
    request_data["test_case_key"] = test_case_key
    request_data["started_at"] = current_time

    # Assign _id
    db_insert = TestExecution(**request_data).model_dump()
    db_insert["_id"] = execution_key

    # Create the test execution in the database
    await db.create(DB_COLLECTION_TE, db_insert)
    
    # Update last_execution_key and updated_at for test case
    tc_data["updated_at"] = current_time
    tc_data["last_execution_key"] = execution_key
    tc_data["last_result"] = request_data["result"]
    await db.update(DB_COLLECTION_TC, tc_data, {
        "project_key": project_key,
        "test_case_key": test_case_key
    })

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
               tags=[DB_COLLECTION_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_execution_by_test_case_key(request: Request,
                                                project_key: str,
                                                test_case_key: str):
    """Delete all test executions for a specific test case within a project"""

    db = request.app.state.mdb

    # Check project exists
    project = await db.find_one(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })
    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Check if test_case_key exists
    tc_data = await db.find_one(DB_COLLECTION_TC, {
        "test_case_key": test_case_key,
        "project_key": project_key
    })
    if tc_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    # TODO: Update cycles and test case before removing execution keys

    # delete all test executions for the specified test case
    result, deleted_count = await db.delete(DB_COLLECTION_TE, {
        "project_key": project_key,
        "test_case_key": test_case_key
    })

    if deleted_count == 0:
        # Test case has no executions
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"No test executions found "
                              f"for test case {test_case_key}"}
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/executions/{{execution_key}}",
            tags=[DB_COLLECTION_TE],
            response_model=TestExecution,
            status_code=status.HTTP_200_OK)
async def get_execution_by_key(request: Request,
                               execution_key: str):
    """Retrieve a specific test execution by its ID"""

    db = request.app.state.mdb

    # Retrieve test execution from database
    test_execution = await db.find_one(DB_COLLECTION_TE, {
        "execution_key": execution_key
    })
    if test_execution is None:
        # test execution not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"}
        )

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_execution)


@router.put(f"/api/{API_VERSION}/tm/executions/{{execution_key}}",
            tags=[DB_COLLECTION_TE],
            response_model=TestExecutionUpdate)
async def update_execution_by_key(request: Request,
                                  execution_key: str,
                                  execution: TestExecutionUpdate):
    """Update a specific test execution by its ID"""

    db = request.app.state.mdb

    # Check execution exists
    response = await get_execution_by_key(request, execution_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data, excluding None values
    request_data = execution.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}

    # Update the execution in the database
    result, matched_count = await db.update(DB_COLLECTION_TE, request_data, {
        "execution_key": execution_key
    })

    if matched_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"})

    # Retrieve the updated test case
    updated_test_execution = await db.find_one(DB_COLLECTION_TE, {
        "execution_key": execution_key
    })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_test_execution)


@router.delete(f"/api/{API_VERSION}/tm/executions/{{execution_key}}",
               tags=[DB_COLLECTION_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution_by_key(request: Request,
                                  execution_key: str):
    """Delete a specific test execution by its ID"""

    db = request.app.state.mdb

    # Delete the project from the database
    result, deleted_count = await db.delete_one(DB_COLLECTION_TE, {
        "execution_key": execution_key
    })

    if deleted_count == 0:
        # Test execution not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"}
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
