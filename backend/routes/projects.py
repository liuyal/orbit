# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/projects.py

from fastapi import APIRouter, Request, status
from pydantic import BaseModel

router = APIRouter()


class Project(BaseModel):
    id: str
    project_key: str
    description: str
    test_cases: int
    test_cycles: int
    created_at: str
    updated_at: str = None
    is_active: bool = True


class ProjectCreate(BaseModel):
    project_key: str
    created_at: str
    description: str = None
    is_active: bool = None


class ProjectUpdate(BaseModel):
    description: str = None
    updated_at: str = None
    is_active: bool = None


@router.get("/api/projects",
            tags=["projects"],
            response_model=list[Project],
            status_code=status.HTTP_200_OK)
async def list_projects(request: Request):
    """Endpoint to get projects"""


@router.post("/api/projects",
             tags=["projects"],
             status_code=status.HTTP_204_NO_CONTENT)
async def create_project(request: Request, project: ProjectCreate):
    """Endpoint to create project."""


@router.get("/api/projects/{project_key}",
            tags=["projects"],
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def get_project(request: Request, project_key: str):
    """Endpoint to get project"""


@router.put("/api/projects/{project_key}",
            tags=["projects"],
            response_model=ProjectUpdate,
            status_code=status.HTTP_200_OK)
async def update_project(request: Request, project_key: str, project: ProjectUpdate):
    """Endpoint to update project"""


@router.delete("/api/projects/{project_key}",
               tags=["projects"],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(request: Request, project_key: str):
    """Endpoint to delete project"""
