# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/cycles.py

import json

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app_def.app_def import (
    DB_COLLECTION_TE,
    DB_COLLECTION_TCY,
    API_VERSION
)
from backend.models.test_cycles import (
    TestCycle,
    TestCycleCreate,
    TestCycleUpdate

)
from backend.routes.projects import get_project_by_key
from backend.routes.test_executions import (
    TestExecution,
    get_execution
)
from backend.tools.tools import get_current_utc_time

router = APIRouter()


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}/cycles",
            tags=[DB_COLLECTION_TCY],
            response_model=list[TestCycle])
async def get_all_cycles_for_project(request: Request,
                                     project_key: str):
    """Get all test cycles for project."""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Retrieve all test cycles from the database matching project_key
    db = request.app.state.db
    test_cycles = await db.find(DB_COLLECTION_TCY,
                                {"project_key": project_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=test_cycles)


@router.post(f"/api/{API_VERSION}/tm/projects/{{project_key}}/cycles",
             tags=[DB_COLLECTION_TCY],
             response_model=TestCycle,
             status_code=status.HTTP_201_CREATED)
async def create_cycle_for_project(request: Request,
                                   project_key: str,
                                   cycle: TestCycleCreate):
    """Create a new test cycle for project."""

    current_time = get_current_utc_time()

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data
    request_data = cycle.model_dump()
    test_cycle_key = request_data["test_cycle_key"]

    # Check if test_cycle already exists
    response = await get_cycle_by_key(request, test_cycle_key)
    if response.status_code != status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"test cycle {test_cycle_key} already exists."})

    # Validate that test_case_key starts with project_key
    if not test_cycle_key.startswith(project_key):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"test_cycle_key  {test_cycle_key} "
                              f"does not belong to project {project_key}"})

    # Initialize counts and timestamps
    request_data["project_key"] = project_key
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time

    # Assign _id
    db_insert = TestCycle(**request_data).model_dump()
    db_insert["_id"] = test_cycle_key

    # Create the test cycle in the database
    db = request.app.state.db
    await db.create(DB_COLLECTION_TCY, db_insert)

    return Response(status_code=status.HTTP_201_CREATED)


@router.get(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
            tags=[DB_COLLECTION_TCY],
            response_model=TestCycle)
async def get_cycle_by_key(request: Request,
                           test_cycle_key: str):
    """Get a specific test cycle by its ID."""

    # Retrieve the test cycle from the database
    db = request.app.state.db
    result = await db.find_one(DB_COLLECTION_TCY,
                               {"test_cycle_key": test_cycle_key})

    if result is None:
        # test case not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test cycle {test_cycle_key} not found"})

    else:
        # test case found
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result)


@router.put(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
            tags=[DB_COLLECTION_TCY],
            response_model=TestCycle)
async def update_cycle_by_key(request: Request,
                              test_cycle_key: str,
                              cycle: TestCycleUpdate):
    """Update a specific test cycle by its ID."""

    current_time = get_current_utc_time()

    # Prepare request data, excluding None values
    request_data = cycle.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["updated_at"] = current_time

    # Update the cycle in the database
    db = request.app.state.db
    result, matched_count = await db.update(
        DB_COLLECTION_TCY,
        {"test_cycle_key": test_cycle_key},
        request_data)

    if matched_count == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test cycle {test_cycle_key} not found"})

    # Retrieve the updated test case
    updated_test_cycle = await db.find_one(
        DB_COLLECTION_TCY,
        {"test_cycle_key": test_cycle_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_test_cycle)


@router.delete(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}",
               tags=[DB_COLLECTION_TCY],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycle_by_key(request: Request,
                              test_cycle_key: str):
    """Delete a specific test cycle by its ID."""

    # Delete the test_cycle from the database
    db = request.app.state.db
    result, deleted_count = await db.delete_one(
        DB_COLLECTION_TCY,
        {"test_cycle_key": test_cycle_key})

    if deleted_count == 0:
        # Test case not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Test cycle {test_cycle_key} not found"})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions",
            tags=[DB_COLLECTION_TCY],
            response_model=list[TestExecution])
async def get_cycle_executions(request: Request,
                               test_cycle_key: str):
    """Get all test executions associated with a specific test cycle."""

    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())
    cycle_executions = cycle_data.get("executions")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=cycle_executions)


@router.post(f"/api/{API_VERSION}/tm/cycles/{{test_cycle_key}}/executions",
             tags=[DB_COLLECTION_TCY],
             status_code=status.HTTP_200_OK)
async def add_execution_to_cycle(request: Request,
                                 test_cycle_key: str,
                                 execution_key: str):
    """Add a test execution to a specific test cycle."""

    # Check cycle exists
    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check execution exists
    response = await get_execution(request, execution_key)
    execution_data = json.loads(response.body.decode())
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check execution not already in cycle
    if execution_key in cycle_data["executions"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Execution {execution_key} "
                              f"already in cycle {test_cycle_key}"})

    # Add execution to cycle
    db = request.app.state.db
    cycle_data["executions"].append(execution_key)
    await db.update(DB_COLLECTION_TCY,
                    {"test_cycle_key": test_cycle_key},
                    cycle_data)

    # Update execution cycle id
    execution_data["test_cycle_key"] = test_cycle_key
    await db.update(DB_COLLECTION_TE,
                    {"execution_key": execution_key},
                    execution_data)

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
    """Remove test executions from a specific test cycle."""

    # Check cycle exists
    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check execution exists
    response = await get_execution(request, execution_key)
    execution_data = json.loads(response.body.decode())
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # remote execution to cycle
    db = request.app.state.db
    cycle_data["executions"] = [e for e in cycle_data["executions"] if e != execution_key]
    await db.update(DB_COLLECTION_TCY,
                    {"test_cycle_key": test_cycle_key},
                    cycle_data)

    # Update execution cycle id
    execution_data["test_cycle_key"] = None
    await db.update(DB_COLLECTION_TE,
                    {"execution_key": execution_key},
                    execution_data)

    # return updated cycle_data
    response = await get_cycle_by_key(request, test_cycle_key)
    cycle_data = json.loads(response.body.decode())

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=cycle_data)
