# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/projects.py

import json

from fastapi import APIRouter, Request, status, Response
from starlette.responses import JSONResponse

from backend.app_def.app_def import DB_COLLECTION_PRJ
from backend.models.projects import (
    Project,
    ProjectCreate,
    ProjectUpdate
)
from backend.routes.test_cases import (
    get_all_test_cases_by_project
)
from backend.tools.tools import (
    get_current_utc_time
)

router = APIRouter()


@router.get("/tm/api/v1/projects",
            tags=[DB_COLLECTION_PRJ],
            response_model=list[Project],
            status_code=status.HTTP_200_OK)
async def get_all_projects(request: Request):
    """Endpoint to get projects"""

    db = request.app.state.db
    projects = await db.find(DB_COLLECTION_PRJ, {})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=projects)


@router.post("/tm/api/v1/projects",
             tags=[DB_COLLECTION_PRJ],
             response_model=Project,
             status_code=status.HTTP_201_CREATED)
async def create_project_by_project_key(request: Request,
                                        project: ProjectCreate):
    """Endpoint to create project."""

    current_time = get_current_utc_time()

    # Prepare request data
    request_data = project.model_dump()

    # Check if project_key already exists
    db = request.app.state.db
    result = await db.find_one(
        DB_COLLECTION_PRJ,
        {"project_key": request_data["project_key"]})

    if result is not None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": f"Project "
                                              f"{request_data['project_key']} "
                                              f"already exists."})

    # Initialize counts and timestamps
    request_data["test_case_count"] = 0
    request_data["test_execution_count"] = 0
    request_data["test_cycle_count"] = 0
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time

    # Assign _id
    db_insert = Project(**request_data).model_dump()
    db_insert["_id"] = request_data["project_key"]
    await db.create(DB_COLLECTION_PRJ, db_insert)

    # Retrieve the updated project
    created_project = await db.find_one(
        DB_COLLECTION_PRJ,
        {"project_key": request_data["project_key"]})

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=created_project)


@router.get("/tm/api/v1/projects/{project_key}",
            tags=[DB_COLLECTION_PRJ],
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def get_project_by_project_key(request: Request,
                                     project_key: str):
    """Endpoint to get project"""

    # Retrieve project from database
    db = request.app.state.db
    result = await db.find_one(
        DB_COLLECTION_PRJ,
        {"project_key": project_key})

    if result is None:
        # Project not found
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": f"Project "
                                              f"{project_key} "
                                              f"not found."})
    else:
        # Convert ObjectId to string
        return JSONResponse(status_code=status.HTTP_200_OK,
                            content=result)


@router.put("/tm/api/v1/projects/{project_key}",
            tags=[DB_COLLECTION_PRJ],
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def update_project_by_project_key(request: Request,
                                        project_key: str,
                                        project_update: ProjectUpdate):
    """Endpoint to update project"""

    current_time = get_current_utc_time()

    # Prepare request data, excluding None values
    request_data = project_update.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["updated_at"] = current_time

    # Update the project in the database
    db = request.app.state.db
    result, matched_count = await db.update(DB_COLLECTION_PRJ,
                                            {"project_key": project_key},
                                            {"$set": request_data})

    if matched_count == 0:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": f"Project {project_key} "
                                              f"not found"})

    # Retrieve the updated project
    updated_project = await db.find_one(DB_COLLECTION_PRJ,
                                        {"project_key": project_key})

    updated = set(request_data.items()).issubset(set(updated_project.items()))

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_project)


@router.delete("/tm/api/v1/projects/{project_key}",
               tags=[DB_COLLECTION_PRJ],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_project_key(request: Request,
                                        project_key: str):
    """Endpoint to delete project"""

    # Get all test-cases for the project
    db = request.app.state.db
    response = await get_all_test_cases_by_project(request, project_key)
    if len(json.loads(response.body.decode())) > 0:
        # There are linked test-cases, cannot delete project
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": f"Project "
                                              f"{project_key} "
                                              f"has linked test-cases. "
                                              f"Cannot delete."})

    # TODO: add check for not existing test-executions, test-cycles linked

    # Delete the project from the database
    result, deleted_count = await db.delete(DB_COLLECTION_PRJ,
                                            {"project_key": project_key})

    if result.deleted_count == 0:
        # Project not found
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": f"Project "
                                              f"{project_key} "
                                              f"not found."})

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/tm/api/v1/projects/{project_key}/nuke",
               tags=[DB_COLLECTION_PRJ],
               status_code=status.HTTP_204_NO_CONTENT)
async def force_delete_project_by_project_key(request: Request,
                                              project_key: str):
    """Endpoint to force delete project"""

    db = request.app.state.db

    # TODO: delete the linked test-cases, test-executions, test-cycles

    # Delete the project from the database
    result, deleted_count = await db.delete(DB_COLLECTION_PRJ,
                                            {"project_key": project_key})

    if deleted_count == 0:
        # Project not found
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": f"Project "
                                              f"{project_key} "
                                              f"not found."})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
