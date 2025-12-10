# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/cycles.py

from fastapi import APIRouter, Request, status

from backend.models.test_cycles import (
    TestCycle,
    TestCycleCreate,
    TestCycleUpdate

)
from backend.app_def.app_def import DB_COLLECTION_TCY
from backend.routes.test_executions import TestExecution

router = APIRouter()


@router.get("/tm/api/v1/cycles",
            tags=[DB_COLLECTION_TCY],
            response_model=list[TestCycle])
async def get_all_cycles(request: Request):
    """Get all test cycles."""


@router.get("/tm/api/v1/projects/{project_key}/cycles",
            tags=[DB_COLLECTION_TCY],
            response_model=list[TestCycle])
async def get_all_cycles_for_project(request: Request,
                                     project_key: str):
    """Get all test cycles for project."""


@router.post("/tm/api/v1/projects/{project_key}/cycles",
             tags=[DB_COLLECTION_TCY],
             response_model=TestCycle,
             status_code=status.HTTP_201_CREATED)
async def create_cycle_for_project(request: Request,
                                   project_key: str,
                                   cycle: TestCycleCreate):
    """Create a new test cycle for project."""


@router.get("/tm/api/v1/cycles/{cycle_key}",
            tags=[DB_COLLECTION_TCY],
            response_model=TestCycle)
async def get_cycle(request: Request,
                    cycle_key: str):
    """Get a specific test cycle by its ID."""


@router.put("/tm/api/v1/cycles/{cycle_key}",
            tags=[DB_COLLECTION_TCY],
            response_model=TestCycle)
async def update_cycle(request: Request,
                       cycle_key: str,
                       cycle: TestCycleUpdate):
    """Update a specific test cycle by its ID."""


@router.delete("/tm/api/v1/cycles/{cycle_key}",
               tags=[DB_COLLECTION_TCY],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycle(request: Request,
                       cycle_key: str):
    """Delete a specific test cycle by its ID."""


@router.get("/tm/api/v1/cycles/{cycle_key}/executions",
            tags=[DB_COLLECTION_TCY],
            response_model=list[TestExecution])
async def get_cycle_executions(request: Request,
                               cycle_key: str):
    """Get all test executions associated with a specific test cycle."""


@router.post("/tm/api/v1/cycles/{cycle_key}/executions",
             tags=[DB_COLLECTION_TCY],
             status_code=status.HTTP_204_NO_CONTENT)
async def add_execution_to_cycle(request: Request,
                                 cycle_key: str,
                                 execution_key: str):
    """Add a test execution to a specific test cycle."""


@router.delete("/tm/api/v1/cycles/{cycle_key}/executions/{execution_id}",
               tags=[DB_COLLECTION_TCY],
               status_code=status.HTTP_204_NO_CONTENT)
async def remove_executions_from_cycle(request: Request,
                                       cycle_key: str,
                                       execution_id: str):
    """Remove all test executions from a specific test cycle."""
