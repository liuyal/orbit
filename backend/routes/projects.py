# routes/projects.py

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class Project(BaseModel):
    name: str
    short_name: str
    description: str
    id: str
    created_at: str
    updated_at: str
    test_cases: int
    test_cycles: int
    is_active: bool = True


class ProjectCreate(BaseModel):
    name: str
    short_name: str
    description: str
    id: str


@router.get("/api/projects",
            tags=["projects"],
            response_model=list[Project])
def list_projects():
    """Endpoint to get projects"""

    projects = {"projects": []}

    return


@router.post("/api/projects",
             tags=["projects"],
             status_code=status.HTTP_201_CREATED,
             response_model=ProjectCreate)
def create_project():
    """Endpoint to create project."""

    return


@router.get("/api/projects/{project_id}",
            tags=["projects"],
            response_model=Project)
def get_project(project_id: str):
    """Endpoint to get project"""

    project = {}

    return


@router.put("/api/projects/{project_id}",
            tags=["projects"],
            response_model=Project)
def update_project(project_id: str):
    """Endpoint to update project"""

    project = {}

    return


@router.delete("/api/projects/{project_id}",
               tags=["projects"],
               status_code=status.HTTP_204_NO_CONTENT, )
def delete_project(project_id: str):
    """Endpoint to delete project"""

    return
