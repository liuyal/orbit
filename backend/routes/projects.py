# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/projects.py

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app.app_def import (
    DB_COLLECTION_PRJ,
    DB_COLLECTION_TC,
    API_VERSION
)
from backend.app.utility import (
    get_current_utc_time
)
from backend.models.projects import (
    Project,
    ProjectCreate,
    ProjectUpdate
)

router = APIRouter()


@router.get(f"/api/{API_VERSION}/tm/projects",
            tags=[DB_COLLECTION_PRJ],
            response_model=list[Project],
            status_code=status.HTTP_200_OK)
async def get_all_projects(request: Request):
    """Endpoint to get projects"""

    # Retrieve all projects from database
    db = request.app.state.mdb
    projects = await db.find(DB_COLLECTION_PRJ, {})

    for project in projects:
        test_cases = await db.find(DB_COLLECTION_TC,
                                   {"project_key": project["project_key"]})
        project["test_case_count"] = len(test_cases)

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=projects)


@router.post(f"/api/{API_VERSION}/tm/projects",
             tags=[DB_COLLECTION_PRJ],
             response_model=Project,
             status_code=status.HTTP_201_CREATED)
async def create_project_by_key(request: Request,
                                project: ProjectCreate):
    """Endpoint to create project."""

    current_time = get_current_utc_time()

    # Prepare request data
    request_data = project.model_dump()
    project_key = request_data["project_key"]

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code != status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Project {project_key} already exists"})

    # Initialize counts and timestamps
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time

    # Assign _id
    db_insert = Project(**request_data).model_dump()
    db_insert["_id"] = project_key

    # Create the project in the database
    db = request.app.state.mdb
    await db.create(DB_COLLECTION_PRJ, db_insert)

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}",
            tags=[DB_COLLECTION_PRJ],
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def get_project_by_key(request: Request,
                             project_key: str):
    """Endpoint to get project"""

    # Retrieve project from database
    db = request.app.state.mdb
    project = await db.find_one(DB_COLLECTION_PRJ,
                                {"project_key": project_key})

    if project is None:
        # Project not found
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"error": f"Project {project_key} not found"})

    test_cases = await db.find(DB_COLLECTION_TC,
                               {"project_key": project["project_key"]})
    project["test_case_count"] = len(test_cases)

    # Convert ObjectId to string
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=project)


@router.put(f"/api/{API_VERSION}/tm/projects/{{project_key}}",
            tags=[DB_COLLECTION_PRJ],
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def update_project_by_key(request: Request,
                                project_key: str,
                                project_update: ProjectUpdate):
    """Endpoint to update project"""

    current_time = get_current_utc_time()

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data, excluding None values
    request_data = project_update.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["updated_at"] = current_time

    # Update the project in the database
    db = request.app.state.mdb
    await db.update(DB_COLLECTION_PRJ,
                    {"project_key": project_key},
                    request_data)

    # Retrieve the updated project
    updated_project = await db.find_one(DB_COLLECTION_PRJ,
                                        {"project_key": project_key})

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_project)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}",
               tags=[DB_COLLECTION_PRJ],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_key(request: Request,
                                project_key: str,
                                force: dict = None):
    """Endpoint to delete project"""

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Get all test-cases for the project
    db = request.app.state.mdb

    if force and force["force"] is False:
        # TODO: add check for not existing test-executions, test-cycles linked
        pass

        # from backend.routes.test_cases import get_all_test_cases_by_project
        # response = await get_all_test_cases_by_project(request, project_key)
        # if len(json.loads(response.body.decode())) > 0:
        #     # There are linked test-cases, cannot delete project
        #     return JSONResponse(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         content={"error": f"Project {project_key} has linked test-cases"})

    else:
        # TODO: Delete all test-cases, executions, cycles linked to project
        pass

    # Delete the project from the database
    await db.delete(DB_COLLECTION_PRJ,
                    {"project_key": project_key})

    return Response(status_code=status.HTTP_204_NO_CONTENT)
