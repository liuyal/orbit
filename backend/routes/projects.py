# routes/projects.py

from docs.projects import (
    GET_RESPONSES,
    POST_RESPONSES,
    PUT_RESPONSES,
    DELETE_RESPONSES
)
from fastapi import APIRouter
from fastapi.responses import (
    JSONResponse,
    Response
)
from models.projects import (
    Project,
    ProjectCreate,
)

router = APIRouter()


@router.get("/api/projects",
            response_model=list[Project],
            responses=GET_RESPONSES)
def list_projects():
    """Endpoint to get projects"""

    projects = {"projects": []}

    return JSONResponse(status_code=200, content=projects)


@router.post("/api/projects",
             status_code=201,
             response_model=ProjectCreate,
             responses=POST_RESPONSES)
def create_project():
    """Endpoint to create project."""

    return JSONResponse(status_code=201, content=None)


@router.get("/api/projects/{project_id}",
            response_model=Project,
            responses=GET_RESPONSES)
def get_project(project_id: str):
    """Endpoint to get project"""

    project = {}

    return JSONResponse(status_code=200, content=project)


@router.put("/api/projects/{project_id}",
            response_model=Project,
            responses=PUT_RESPONSES)
def update_project(project_id: str):
    """Endpoint to update project"""

    project = {}

    return JSONResponse(status_code=200, content=project)


@router.delete("/api/projects/{project_id}",
               status_code=204,
               responses=DELETE_RESPONSES)
def delete_project(project_id: str):
    """Endpoint to delete project"""

    return Response(status_code=204)
