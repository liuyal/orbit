# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/cycles.py

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from backend.routes.executions import TestExecution

router = APIRouter()


class TestCycle(BaseModel):
    id: str
    cycle_key: str
    project_key: str
    title: str
    description: str
    created_at: str
    updated_at: str = None
    status: dict[str, int] = None
    executions: list[str] = []
    test_cases: list[str] = []


class TestCycleCreate(BaseModel):
    cycle_key: str
    project_key: str
    title: str
    description: str = None
    created_at: str
    updated_at: str = None
    status: dict[str, int] = None


class TestCycleUpdate(BaseModel):
    cycle_key: str = None
    title: str = None
    description: str = None
    updated_at: str = None
    status: dict[str, int] = None
    executions: list[str] = []
    test_cases: list[str] = []


@router.get("/api/cycles/",
            tags=["cycles"],
            response_model=list[TestCycle])
async def list_cycles(request: Request):
    """List all test cycles."""


@router.post("/api/cycles/",
             tags=["cycles"],
             response_model=TestCycle,
             status_code=status.HTTP_201_CREATED)
async def create_cycle(request: Request,
                       cycle: TestCycleCreate):
    """Create a new test cycle."""


@router.get("/api/cycles/{cycle_key}",
            tags=["cycles"],
            response_model=TestCycle)
async def get_cycle(request: Request,
                    cycle_key: str):
    """Get a specific test cycle by its ID."""


@router.put("/api/cycles/{cycle_key}",
            tags=["cycles"],
            response_model=TestCycle)
async def update_cycle(request: Request,
                       cycle_key: str,
                       cycle: TestCycleUpdate):
    """Update a specific test cycle by its ID."""


@router.delete("/api/cycles/{cycle_key}",
               tags=["cycles"],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycle(request: Request,
                       cycle_key: str):
    """Delete a specific test cycle by its ID."""


# List Cycle Executions
@router.get("/api/cycles/{cycle_key}/executions",
            tags=["cycles"],
            response_model=list[TestExecution])
async def list_cycle_executions(request: Request,
                                cycle_key: str):
    """List all test executions associated with a specific test cycle."""


# Add Execution To Cycle
@router.post("/api/cycles/{cycle_key}/executions",
             tags=["cycles"],
             status_code=status.HTTP_204_NO_CONTENT)
async def add_execution_to_cycle(request: Request,
                                 cycle_key: str,
                                 execution_key: str):
    """Add a test execution to a specific test cycle."""


@router.delete("/api/cycles/{cycle_key}/executions/{execution_id}",
               tags=["cycles"],
               status_code=status.HTTP_204_NO_CONTENT)
async def remove_executions_from_cycle(request: Request,
                                       cycle_key: str,
                                       execution_id: str):
    """Remove all test executions from a specific test cycle."""
