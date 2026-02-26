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
    DB_COLLECTION_TE,
    DB_COLLECTION_TCY,
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

    db = request.app.state.mdb

    # Retrieve all projects from database
    projects = await db.find(DB_COLLECTION_PRJ, {})

    for project in projects:
        # Get count for test cases and cycles
        test_cases = await db.find(DB_COLLECTION_TC, {
            "project_key": project["project_key"]
        })
        test_cycles = await db.find(DB_COLLECTION_TCY, {
            "project_key": project["project_key"]
        })

        # Assign value to dict
        project["test_case_count"] = len(test_cases)
        project["test_cycle_count"] = len(test_cycles)

        # Update count back into DB
        await db.update(DB_COLLECTION_PRJ, project, {
            "project_key": project["project_key"]
        })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=projects)


@router.post(f"/api/{API_VERSION}/tm/projects",
             tags=[DB_COLLECTION_PRJ],
             response_model=Project,
             status_code=status.HTTP_201_CREATED)
async def create_project_by_key(request: Request,
                                project: ProjectCreate):
    """Endpoint to create project"""

    db = request.app.state.mdb

    # Prepare request data
    request_data = project.model_dump()
    project_key = request_data["project_key"]

    # Check for duplicate labels
    if len(request_data["labels"]) != len(set(request_data["labels"])):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Duplicate labels are not allowed"}
        )

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code != status.HTTP_404_NOT_FOUND:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"{project_key} already exists"}
        )

    # Initialize counts and timestamps
    current_time = get_current_utc_time()
    request_data["created_at"] = current_time
    request_data["updated_at"] = current_time
    request_data["test_case_count"] = 0
    request_data["test_cycle_count"] = 0

    # Assign _id
    db_insert = Project(**request_data).model_dump()
    db_insert["_id"] = project_key

    # Create the project in the database
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

    db = request.app.state.mdb

    # Retrieve project from database
    project = await db.find_one(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })
    if project is None:
        # Project not found
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Get count of test cases and cycles
    test_cases = await db.find(DB_COLLECTION_TC, {
        "project_key": project_key
    })
    test_cycles = await db.find(DB_COLLECTION_TCY, {
        "project_key": project_key
    })

    # Assign to project
    project["test_case_count"] = len(test_cases)
    project["test_cycle_count"] = len(test_cycles)

    # Update count back into DB
    await db.update(DB_COLLECTION_PRJ, project, {
        "project_key": project_key
    })

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

    db = request.app.state.mdb

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Prepare request data, excluding None values
    request_data = project_update.model_dump()
    request_data = {k: v for k, v in request_data.items() if v is not None}
    request_data["updated_at"] = get_current_utc_time()

    # Check for duplicate labels
    if len(request_data["labels"]) != len(set(request_data["labels"])):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": f"Duplicate labels are not allowed"}
        )

    # Get count of test cases and cycles
    test_cases = await db.find(DB_COLLECTION_TC, {
        "project_key": project_key
    })
    test_cycles = await db.find(DB_COLLECTION_TCY, {
        "project_key": project_key
    })

    # Assign value to dict
    request_data["test_case_count"] = len(test_cases)
    request_data["test_cycle_count"] = len(test_cycles)

    # Update count back into DB
    await db.update(DB_COLLECTION_PRJ, request_data, {
        "project_key": project_key
    })

    # Retrieve the updated project
    updated_project = await db.find_one(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_project)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}",
               tags=[DB_COLLECTION_PRJ],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_key(request: Request,
                                project_key: str,
                                force: dict = None):
    """Endpoint to delete project"""

    db = request.app.state.mdb

    # Check project exists
    response = await get_project_by_key(request, project_key)
    if response.status_code == status.HTTP_404_NOT_FOUND:
        return response

    # Check force flag
    if force and force.get("force", None) is False:
        # Check for existing test cases, test-executions, test-cycles linked to the project
        test_case_count = await db.count(DB_COLLECTION_TC, {
            "project_key": project_key
        })
        if test_case_count > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Project {project_key} "
                                  f"contains linked test-cases"}
            )

        test_executions_count = await db.count(DB_COLLECTION_TE, {
            "project_key": project_key
        })
        if test_executions_count > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Project {project_key} "
                                  f"contains linked test-executions"}
            )

        test_cycles_count = await db.count(DB_COLLECTION_TCY, {
            "project_key": project_key
        })
        if test_cycles_count > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Project {project_key} "
                                  f"contains linked test-cycles"}
            )

    else:
        # Force delete all linked test-cases, test-executions, test-cycles
        await db.delete(DB_COLLECTION_TCY, {
            "project_key": project_key
        })
        await db.delete(DB_COLLECTION_TE, {
            "project_key": project_key
        })
        await db.delete(DB_COLLECTION_TC, {
            "project_key": project_key
        })

    # Delete the project from the database
    await db.delete(DB_COLLECTION_PRJ, {
        "project_key": project_key
    })

    return Response(status_code=status.HTTP_204_NO_CONTENT)
