# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/cycles.py

import asyncio
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
    API_VERSION,
    DB_COLLECTION_TM_PRJ,
    DB_COLLECTION_TM_TE,
    DB_COLLECTION_TM_TC,
    DB_COLLECTION_TM_TCY,
    DB_NAME_TM,
    TCY_KEY_PREFIX
)
from backend.app.utility import (
    get_current_utc_time,
    calculate_cycle_status
)
from backend.models.test_cycles import (
    TestCycle,
    TestCycleCreate,
    TestCycleUpdate
)

router = APIRouter()

DB_NAME_TM = DB_NAME_TM.name
DB_COLLECTION_TM_PRJ = DB_COLLECTION_TM_PRJ.name
DB_COLLECTION_TM_TC = DB_COLLECTION_TM_TC.name
DB_COLLECTION_TM_TE = DB_COLLECTION_TM_TE.name
DB_COLLECTION_TM_TCY = DB_COLLECTION_TM_TCY.name


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/cycles",
            tags=[DB_COLLECTION_TM_TCY],
            response_model=list[TestCycle],
            status_code=status.HTTP_200_OK)
async def get_all_cycles_for_project(request: Request,
                                     project_key: str):
    """Get all test cycles for project"""

    db = request.app.state.mdb

    # Concurrently check project exists and fetch cycles
    project, test_cycles = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.find(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    test_cycles = test_cycles[::-1]

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cycles)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/cycles",
             tags=[DB_COLLECTION_TM_TCY],
             response_model=TestCycle,
             status_code=status.HTTP_201_CREATED)
async def create_cycle_for_project(request: Request,
                                   project_key: str,
                                   cycle: Optional[TestCycleCreate] = None):
    """Create a new test cycle for project"""

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

    if cycle:
        # Prepare request data from request data
        request_data = cycle.model_dump()
        test_cycle_key = request_data.get("test_cycle_key", None)

    else:
        # Prepare default request data
        request_data = TestCycleCreate().model_dump()
        test_cycle_key = None

    if test_cycle_key is None:
        # Auto-generate test_cycle_key using an atomic per-project counter.
        seq = await db.get_next_sequence(DB_NAME_TM, f"{project_key}_tcy")
        test_cycle_key = f"{project_key}-{TCY_KEY_PREFIX}{seq}"
        request_data["test_cycle_key"] = test_cycle_key

    else:
        # regex check for valid test_cycle_key format, must be PRJ_KEY-C###
        pattern = rf"^{project_key}-{TCY_KEY_PREFIX}\d+$"
        if not re.match(pattern, test_cycle_key):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"test cycle key '{test_cycle_key}' is not valid. "
                                  f"Must be in format {project_key}-{TCY_KEY_PREFIX}#"}
            )

        # Check if test_cycle already exists with direct find_one
        existing = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TCY, {
            "test_cycle_key": test_cycle_key
        })
        if existing is not None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"{test_cycle_key} already exists"}
            )

        # Advance the counter so future auto-generated keys never collide with
        # manually-provided ones (e.g. user inserts C1, C2, C4 manually, then
        # two auto-inserts must start at C5 not C3/C4).
        manual_num = int(test_cycle_key.split(TCY_KEY_PREFIX)[-1])
        await db.sync_sequence(DB_NAME_TM, f"{project_key}_tcy", manual_num)

    # Initialize counts and timestamps
    current_time = get_current_utc_time()
    request_data["project_key"] = project_key
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time

    # Assign _id
    db_insert = TestCycle(**request_data).model_dump()
    db_insert["_id"] = test_cycle_key

    # Create the test cycle in the database
    await db.create(DB_NAME_TM, DB_COLLECTION_TM_TCY, db_insert)

    # Update project test cycle count using db.count (no full document fetch)
    project["test_cycle_count"] = await db.count(DB_NAME_TM, DB_COLLECTION_TM_TCY, {
        "project_key": project_key
    })
    await db.update(DB_NAME_TM, DB_COLLECTION_TM_PRJ, project, {
        "project_key": project_key
    })

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)


@router.get(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
            tags=[DB_COLLECTION_TM_TCY],
            response_model=TestCycle,
            status_code=status.HTTP_200_OK)
async def get_cycle_by_key(request: Request,
                           test_cycle_key: str):
    """Get a specific test cycle by its ID"""

    db = request.app.state.mdb

    # Retrieve the test cycle from the database
    result = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TCY, {
        "test_cycle_key": test_cycle_key
    })

    if result is None:
        # test case not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    else:
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=result)


@router.put(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
            tags=[DB_COLLECTION_TM_TCY],
            response_model=TestCycle,
            status_code=status.HTTP_200_OK)
async def update_cycle_by_key(request: Request,
                              test_cycle_key: str,
                              cycle: TestCycleUpdate):
    """Update a specific test cycle by its ID"""

    db = request.app.state.mdb

    # Prepare request data, excluding None values
    request_data = cycle.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["updated_at"] = get_current_utc_time()

    # Update the cycle in the database
    result, matched_count = await db.update(DB_NAME_TM, DB_COLLECTION_TM_TCY, request_data, {
        "test_cycle_key": test_cycle_key
    })

    if matched_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    # Retrieve the updated test case
    updated_test_cycle = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TCY, {
        "test_cycle_key": test_cycle_key
    })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_test_cycle)


@router.delete(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
               tags=[DB_COLLECTION_TM_TCY],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycle_by_key(request: Request,
                              test_cycle_key: str):
    """Delete a specific test cycle by its ID"""

    db = request.app.state.mdb

    # Check cycle exists
    result = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TCY, {
        "test_cycle_key": test_cycle_key
    })
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    # Concurrently: delete the cycle and clear test_cycle_key on all linked executions
    await asyncio.gather(
        db.delete_one(DB_NAME_TM, DB_COLLECTION_TM_TCY,
                      {"test_cycle_key": test_cycle_key}),
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TE,
                  {"test_cycle_key": None},
                  {"test_cycle_key": test_cycle_key})
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions",
            tags=[DB_COLLECTION_TM_TCY],
            response_model=dict,
            status_code=status.HTTP_200_OK)
async def get_cycle_executions(request: Request,
                               test_cycle_key: str):
    """Get all test executions associated with a specific test cycle"""

    db = request.app.state.mdb

    response = await get_cycle_by_key(request, test_cycle_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    cycle_data = json.loads(response.body)
    cycle_executions = cycle_data.get("executions")

    if not cycle_executions or len(cycle_executions) == 0:
        return JSONResponse(status_code=status.HTTP_200_OK, content={})

    # Query 1: batch fetch all executions by execution_key
    exec_keys = list(cycle_executions.keys())
    executions_list = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TE, {
        "execution_key": {"$in": exec_keys}
    })

    # Extract test_case_keys from execution docs for second batch query
    tc_keys = [e["test_case_key"] for e in executions_list if "test_case_key" in e]

    # Query 2: batch fetch all linked test cases by test_case_key
    test_cases_list = await db.find(DB_NAME_TM, DB_COLLECTION_TM_TC, {
        "test_case_key": {"$in": tc_keys}
    })

    # Build O(1) lookup maps
    test_cases_map = {t["test_case_key"]: t for t in test_cases_list}

    # Merge execution and test case data, keyed by execution_key
    result_data = {}
    for exec_doc in executions_list:
        tc_key = exec_doc.get("test_case_key")
        merged = {**exec_doc, **test_cases_map.get(tc_key, {})}
        result_data[exec_doc["execution_key"]] = merged

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=result_data)


@router.post(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions",
             tags=[DB_COLLECTION_TM_TCY],
             status_code=status.HTTP_200_OK)
async def add_execution_to_cycle(request: Request,
                                 test_cycle_key: str,
                                 execution_key: str):
    """Add a test execution to a specific test cycle"""

    db = request.app.state.mdb

    # Concurrently fetch cycle and execution
    cycle_data, test_execution = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"test_cycle_key": test_cycle_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TE, {"execution_key": execution_key})
    )

    if cycle_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    if test_execution is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"}
        )

    # check execution project matches cycle project
    if test_execution["project_key"] != cycle_data["project_key"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Execution {execution_key} "
                              f"belongs to different project "
                              f"{test_execution['project_key']}"}
        )

    # Check execution does not have cycle already
    if test_execution.get("test_cycle_key", None) is not None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Execution {execution_key} "
                              f"already in cycle "
                              f"{test_execution['test_cycle_key']}"}
        )

    # Check execution not already in cycle
    if test_execution["test_case_key"] in cycle_data["executions"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Execution {execution_key} "
                              f"already in cycle {test_cycle_key}"}
        )

    # Add execution to cycle
    exec_data = {execution_key: test_execution["result"]}
    cycle_data["executions"].update(exec_data)
    cycle_data = calculate_cycle_status(cycle_data)

    # Update execution cycle id and cycle data concurrently
    test_execution["test_cycle_key"] = test_cycle_key
    await asyncio.gather(
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TCY, cycle_data, {"test_cycle_key": test_cycle_key}),
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TE, test_execution, {"execution_key": execution_key})
    )

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=cycle_data)


@router.delete(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions/{{execution_key}}",
               tags=[DB_COLLECTION_TM_TCY],
               status_code=status.HTTP_200_OK)
async def remove_executions_from_cycle(request: Request,
                                       test_cycle_key: str,
                                       execution_key: str):
    """Remove test executions from a specific test cycle"""

    db = request.app.state.mdb

    # Concurrently fetch cycle and execution
    cycle_data, test_execution = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"test_cycle_key": test_cycle_key}),
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_TE, {"execution_key": execution_key})
    )

    if cycle_data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    if test_execution is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{execution_key} not found"}
        )

    # Check execution in cycle
    if test_execution["test_case_key"] not in cycle_data["executions"]:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Execution {execution_key} "
                              f"not in cycle {test_cycle_key}"}
        )

    # Remove execution from cycle
    cycle_data["executions"].pop(test_execution["test_case_key"])

    # Update cycle and clear execution's cycle key concurrently
    test_execution["test_cycle_key"] = None
    await asyncio.gather(
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TCY, cycle_data, {"test_cycle_key": test_cycle_key}),
        db.update(DB_NAME_TM, DB_COLLECTION_TM_TE, test_execution, {"execution_key": execution_key})
    )

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=cycle_data)
