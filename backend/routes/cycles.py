# routes/cycles.py

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class TestCycle(BaseModel):
    id: str
    name: str


class TestCycleCreate(BaseModel):
    name: str


class TestCycleUpdate(BaseModel):
    name: str


class TestExecution(BaseModel):
    id: str
    result: str


class CycleExecutionLink(BaseModel):
    execution_id: str


# List Cycles
@router.get("/api/cycles/",
            tags=["cycles"],
            response_model=list[TestCycle])
def list_cycles():
    return


# Create Cycle
@router.post("/api/cycles/",
             tags=["cycles"],
             response_model=TestCycle,
             status_code=status.HTTP_201_CREATED)
def create_cycle(cycle: TestCycleCreate):
    return


# Get Cycle
@router.get("/api/cycles/{cycle_id}",
            tags=["cycles"],
            response_model=TestCycle)
def get_cycle(cycle_id: str):
    return


# Update Cycle
@router.put("/api/cycles/{cycle_id}",
            tags=["cycles"],
            response_model=TestCycle)
def update_cycle(cycle_id: str, cycle: TestCycleUpdate):
    return


# Delete Cycle
@router.delete("/api/cycles/{cycle_id}",
               tags=["cycles"],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_cycle(cycle_id: str):
    return


# List Cycle Executions
@router.get("/api/cycles/{cycle_id}/executions",
            tags=["cycles"],
            response_model=list[TestExecution])
def list_cycle_executions(cycle_id: str):
    return


# Add Execution To Cycle
@router.post("/api/cycles/{cycle_id}/executions",
             tags=["cycles"],
             response_model=TestExecution,
             status_code=status.HTTP_201_CREATED)
def add_execution_to_cycle(cycle_id: str,
                           link: CycleExecutionLink):
    return


# Delete Cycle Executions
@router.delete("/api/cycles/{cycle_id}/executions",
               tags=["cycles"],
               status_code=status.HTTP_204_NO_CONTENT)
def remove_executions_from_cycle(cycle_id: str):
    return
