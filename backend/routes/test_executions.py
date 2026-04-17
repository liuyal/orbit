# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/execution.py

import asyncio
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
    API_VERSION,
    DB_COLLECTION_TM_PRJ,
    DB_COLLECTION_TM_TE,
    DB_COLLECTION_TM_TC,
    DB_COLLECTION_TM_TCY,
    DB_NAME_TM,
    TE_KEY_PREFIX
)
from backend.app.utility import (
    get_current_utc_time,
    calculate_cycle_status
)
from backend.models.test_executions import (
    TestExecution,
    TestExecutionCreate,
    TestExecutionUpdate
)

router = APIRouter()

DB_NAME_TM = DB_NAME_TM.name
DB_COLLECTION_TM_PRJ = DB_COLLECTION_TM_PRJ.name
DB_COLLECTION_TM_TC = DB_COLLECTION_TM_TC.name
DB_COLLECTION_TM_TE = DB_COLLECTION_TM_TE.name
DB_COLLECTION_TM_TCY = DB_COLLECTION_TM_TCY.name


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/executions",
            tags=[DB_COLLECTION_TM_TE],
            response_model=list[TestExecution],
            status_code=status.HTTP_200_OK)
async def get_all_executions_by_project(request: Request,
                                        project_key: str):
    """Get all test executions for a specific test case within a project"""

    db = request.app.state.mdb

    # Concurrently check project exists and fetch executions
    project, test_executions = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find(DB_NAME_TM, DB_COLLECTION_TM_TE, {"project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )


    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_executions)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/executions",
               tags=[DB_COLLECTION_TM_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_test_execution_by_project(request: Request,
                                               project_key: str):
    """Delete all test executions in the specified project"""

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

    current_time = get_current_utc_time()

    # Concurrently: reset all test cases, reset all cycles, delete all executions
    await asyncio.gather(
        # Bulk reset last_execution_key and last_result on all test cases in project
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TC,
                  {"last_execution_key": None,
                   "last_result": "NOT_EXECUTED",
                   "updated_at": current_time},
                  {"project_key": project_key}),

        # Bulk reset executions map on all cycles in project
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TCY,
                  {"executions": {}, "updated_at": current_time},
                  {"project_key": project_key}),

        # Delete all executions for the project
        db.delete(DB_NAME_TM, DB_COLLECTION_TM_TE,
                  {"project_key": project_key})
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
            tags=[DB_COLLECTION_TM_TE],
            response_model=list[TestExecution],
            status_code=status.HTTP_200_OK)
async def get_all_executions_by_test_case_key(request: Request,
                                              project_key: str,
                                              test_case_key: str):
    """Get all test executions for a specific test case within a project"""

    db = request.app.state.mdb

    # Concurrently check project and test case exist
    project, tc_data = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {"test_case_key": test_case_key,
                                                       "project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    if tc_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    # Retrieve test executions matching project_key and test_case_key
    test_executions = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TE, {
        "project_key": project_key,
        "test_case_key": test_case_key
    })

    test_executions = list(reversed(test_executions))

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_executions)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
             tags=[DB_COLLECTION_TM_TE],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
async def create_execution_by_test_case_key(request: Request,
                                            project_key: str,
                                            test_case_key: str,
                                            execution: Optional[TestExecutionCreate] = None):
    """Create a new test execution for a specific test case within a project"""

    db = request.app.state.mdb

    # Concurrently check project and test case exist
    project, tc_data = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {"test_case_key": test_case_key,
                                                       "project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    if tc_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    if execution:
        request_data = execution.model_dump()
        execution_key = request_data.get("execution_key", None)

    else:
        request_data = TestExecutionCreate().model_dump()
        execution_key = None

    if execution_key is None:
        # Auto-generate execution_key — fetch only _id fields (projection), no full documents
        existing_keys = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TE,
                                      {"project_key": project_key},
                                      {"_id": 1})
        if len(existing_keys) < 1:
            last_te = 1

        else:
            key_n = [int(e["_id"].split(TE_KEY_PREFIX)[-1]) for e in existing_keys]
            last_te = max(key_n) + 1

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

        # Check if execution_key already exists with direct find_one
        existing = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TE, {
            "execution_key": execution_key
        })
        if existing is not None:
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
    await db.create(DB_NAME_TM, DB_COLLECTION_TM_TE, db_insert)

    # Update last_execution_key and updated_at for test case
    tc_data["updated_at"] = current_time
    tc_data["last_execution_key"] = execution_key
    tc_data["last_result"] = request_data["result"]
    await db.update(DB_NAME_TM, DB_COLLECTION_TM_TC, tc_data, {
        "project_key": project_key,
        "test_case_key": test_case_key
    })

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}/test-cases/{{test_case_key}}/executions",
               tags=[DB_COLLECTION_TM_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_execution_by_test_case_key(request: Request,
                                                project_key: str,
                                                test_case_key: str):
    """Delete all test executions for a specific test case within a project"""

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

    # Check if test_case_key exists
    tc_data = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {
        "test_case_key": test_case_key,
        "project_key": project_key
    })
    if tc_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )

    # Check project exists
    test_cycles = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TCY, {
        "project_key": project_key
    })
    for cycle in test_cycles:
        if test_case_key in cycle.get("executions", {}):
            # remove execution key from cycle
            cycle["executions"].pop(test_case_key)
            cycle["updated_at"] = get_current_utc_time()
            await db.update(DB_NAME_TM, DB_COLLECTION_TM_TCY, cycle, {
                "test_cycle_key": cycle["test_cycle_key"]
            })

    # Update test case info
    tc_data["updated_at"] = get_current_utc_time()
    tc_data["last_execution_key"] = None
    tc_data["last_result"] = "NOT_EXECUTED"
    await db.update(DB_NAME_TM, DB_COLLECTION_TM_TC, tc_data, {
        "project_key": project_key,
        "test_case_key": test_case_key
    })

    # Delete all test executions for the specified test case
    result, deleted_count = await db.delete(DB_NAME_TM, DB_COLLECTION_TM_TE, {
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
            tags=[DB_COLLECTION_TM_TE],
            response_model=TestExecution,
            status_code=status.HTTP_200_OK)
async def get_execution_by_key(request: Request,
                               execution_key: str):
    """Retrieve a specific test execution by its ID"""

    db = request.app.state.mdb

    # Retrieve test execution from database
    test_execution = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TE, {
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
            tags=[DB_COLLECTION_TM_TE],
            response_model=TestExecution)
async def update_execution_by_key(request: Request,
                                  execution_key: str,
                                  execution: TestExecutionUpdate):
    """Update a specific test execution by its ID"""

    db = request.app.state.mdb

    # Fetch execution directly to get doc and check existence in one call
    existing_execution = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TE, {
        "execution_key": execution_key
    })
    if existing_execution is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"}
        )

    # Prepare request data, excluding None values
    request_data = execution.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["result"] = request_data["result"].upper()

    # Update the execution in the database
    result, matched_count = await db.update(DB_NAME_TM, DB_COLLECTION_TM_TE, request_data, {
        "execution_key": execution_key
    })
    if matched_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"})

    # Reuse already-fetched execution doc to extract keys — no re-fetch needed
    test_case_key = existing_execution["test_case_key"]
    cycle_key = existing_execution["test_cycle_key"]

    # Concurrently fetch linked test case and cycle
    tc_data, cycle_data = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {"test_case_key": test_case_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"test_cycle_key": cycle_key})
    )

    if tc_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_case_key} not found"}
        )
    if cycle_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{cycle_key} not found"}
        )

    # Prepare test case and cycle updates
    current_time = get_current_utc_time()
    tc_data["last_result"] = request_data["result"]
    cycle_data["executions"][execution_key] = request_data["result"].upper()
    cycle_data = calculate_cycle_status(cycle_data)
    cycle_data["updated_at"] = current_time

    # Apply both updates concurrently
    await asyncio.gather(
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TC, tc_data, {"test_case_key": test_case_key}),
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TCY, cycle_data, {"test_cycle_key": cycle_key})
    )

    # Return the updated execution (merge request_data into existing doc)
    existing_execution.update(request_data)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=existing_execution)


@router.delete(f"/api/{API_VERSION}/tm/executions/{{execution_key}}",
               tags=[DB_COLLECTION_TM_TE],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution_by_key(request: Request,
                                  execution_key: str):
    """Delete a specific test execution by its ID"""

    db = request.app.state.mdb

    # Update test case info if last_execution_key matches the deleted execution
    test_execution = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TE, {
        "execution_key": execution_key
    })
    if test_execution is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"}
        )

    # Check linked test case
    test_case = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TC, {
        "test_case_key": test_execution["test_case_key"]
    })
    if test_case is not None and test_case["last_execution_key"] == execution_key:
        # Update test case info
        test_case["updated_at"] = get_current_utc_time()
        test_case["last_execution_key"] = None
        test_case["last_result"] = "NOT_EXECUTED"
        await db.update(DB_NAME_TM, DB_COLLECTION_TM_TC, test_case, {
            "test_case_key": test_execution["test_case_key"]
        })

    # Delete the execution from the database
    await db.delete_one(DB_NAME_TM, DB_COLLECTION_TM_TE, {
        "execution_key": execution_key
    })

    return Response(status_code=status.HTTP_204_NO_CONTENT)
