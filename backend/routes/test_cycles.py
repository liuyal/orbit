# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/cycles.py

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
    TCY_KEY_PREFIX,
    API_VERSION
)
from backend.app.utility import get_current_utc_time
from backend.models.test_cycles import (
    TestCycle,
    TestCycleCreate,
    TestCycleUpdate

)

router = APIRouter()


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/cycles",
            tags=[DB_COLLECTION_TCY],
            response_model=list[TestCycle],
            status_code=status.HTTP_200_OK)
async def get_all_cycles_for_project(request: Request,
                                     project_key: str):
    """Get all test cycles for project"""

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

    # Retrieve all test cycles from the database matching project_key
    test_cycles = await db.find(DB_COLLECTION_TCY, {
        "project_key": project_key
    })

    test_cycles = list(reversed(test_cycles))

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cycles)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/cycles",
             tags=[DB_COLLECTION_TCY],
             response_model=TestCycle,
             status_code=status.HTTP_201_CREATED)
async def create_cycle_for_project(request: Request,
                                   project_key: str,
                                   cycle: Optional[TestCycleCreate] = None):
    """Create a new test cycle for project"""

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

    if cycle:
        # Prepare request data from request data
        request_data = cycle.model_dump()
        test_cycle_key = request_data.get("test_cycle_key", None)

    else:
        # Prepare default request data
        request_data = TestCycleCreate().model_dump()
        test_cycle_key = None

    if test_cycle_key is None:
        # Auto-generate test_cycle_key
        # get list of test cycle in project to determine next key
        response = await get_all_cycles_for_project(request, project_key)
        cycle = json.loads(response.body.decode())
        if len(cycle) < 1:
            # no test cycle exist yet, start with 1
            last_tcy = 1

        else:
            # extract numeric part of test_cycle_key to find last number
            key_n = [int(c["_id"].split(TCY_KEY_PREFIX)[-1]) for c in cycle]
            last_tcy = max(key_n) + 1

        test_cycle_key = f"{project_key}-{TCY_KEY_PREFIX}{last_tcy}"
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

        # Check if test_cycle already exists
        response = await get_cycle_by_key(request, test_cycle_key)
        if response.status_code != status.HTTP_404_NOT_FOUND:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"{test_cycle_key} already exists"}
            )

    # Initialize counts and timestamps
    current_time = get_current_utc_time()
    request_data["project_key"] = project_key
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time

    # Assign _id
    db_insert = TestCycle(**request_data).model_dump()
    db_insert["_id"] = test_cycle_key

    # Create the test cycle in the database
    await db.create(DB_COLLECTION_TCY, db_insert)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)


@router.get(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
            tags=[DB_COLLECTION_TCY],
            response_model=TestCycle,
            status_code=status.HTTP_200_OK)
async def get_cycle_by_key(request: Request,
                           test_cycle_key: str):
    """Get a specific test cycle by its ID"""

    db = request.app.state.mdb

    # Retrieve the test cycle from the database
    result = await db.find_one(DB_COLLECTION_TCY, {
        "test_cycle_key": test_cycle_key
    })

    if result is None:
        # test case not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    else:
        # test case found
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=result)


@router.put(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
            tags=[DB_COLLECTION_TCY],
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
    result, matched_count = await db.update(DB_COLLECTION_TCY, request_data, {
        "test_cycle_key": test_cycle_key
    })

    if matched_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    # Retrieve the updated test case
    updated_test_cycle = await db.find_one(DB_COLLECTION_TCY, {
        "test_cycle_key": test_cycle_key
    })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_test_cycle)


@router.delete(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
               tags=[DB_COLLECTION_TCY],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycle_by_key(request: Request,
                              test_cycle_key: str):
    """Delete a specific test cycle by its ID"""

    db = request.app.state.mdb

    # Delete the test_cycle from the database
    result, deleted_count = await db.delete_one(DB_COLLECTION_TCY, {
        "test_cycle_key": test_cycle_key
    })

    if deleted_count == 0:
        # Test case not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{test_cycle_key} not found"}
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions",
            tags=[DB_COLLECTION_TCY],
            response_model=list[dict],
            status_code=status.HTTP_200_OK)
async def get_cycle_executions(request: Request,
                               test_cycle_key: str):
    """Get all test executions associated with a specific test cycle"""

    db = request.app.state.mdb

    response = await get_cycle_by_key(request, test_cycle_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    cycle_data = json.loads(response.body.decode())
    cycle_executions = cycle_data.get("executions")

    result_data = {}
    for tc_key, exec_key in cycle_executions.items():
        # Retrieve test execution data
        exec_data = await db.find_one(DB_COLLECTION_TE, {
            "execution_key": exec_key["execution_key"]
        })
        tc_data = await db.find_one(DB_COLLECTION_TC, {
            "test_case_key": tc_key
        })
        exec_data.update(tc_data)

        result_data[tc_key] = exec_data

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=result_data)


@router.post(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions",
             tags=[DB_COLLECTION_TCY],
             status_code=status.HTTP_200_OK)
async def add_execution_to_cycle(request: Request,
                                 test_cycle_key: str,
                                 execution_key: str):
    """Add a test execution to a specific test cycle"""

    db = request.app.state.mdb

    # Check cycle exists
    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check execution exists
    test_execution = await db.find_one(DB_COLLECTION_TE, {
        "execution_key": execution_key
    })
    if test_execution is None:
        # test execution not found
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
    exec_data = {test_execution["test_case_key"]: {
        "execution_key": execution_key
    }}
    cycle_data["executions"].update(exec_data)
    await db.update(DB_COLLECTION_TCY, cycle_data, {
        "test_cycle_key": test_cycle_key
    })

    # Update execution cycle id
    test_execution["test_cycle_key"] = test_cycle_key
    await db.update(DB_COLLECTION_TE, test_execution, {
        "execution_key": execution_key
    })

    # return updated cycle_data
    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=cycle_data)


@router.delete(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions/{{execution_key}}",
               tags=[DB_COLLECTION_TCY],
               status_code=status.HTTP_200_OK)
async def remove_executions_from_cycle(request: Request,
                                       test_cycle_key: str,
                                       execution_key: str):
    """Remove test executions from a specific test cycle"""

    db = request.app.state.mdb

    # Check cycle exists
    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check execution exists
    test_execution = await db.find_one(DB_COLLECTION_TE, {
        "execution_key": execution_key
    })

    if test_execution is None:
        # test execution not found
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
    await db.update(DB_COLLECTION_TCY, cycle_data, {
        "test_cycle_key": test_cycle_key
    })

    # Update execution cycle key
    test_execution["test_cycle_key"] = None
    await db.update(DB_COLLECTION_TE, test_execution, {
        "execution_key": execution_key
    })

    # return updated cycle_data
    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=cycle_data)
