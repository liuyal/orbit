# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/projects.py

import asyncio

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from starlette.responses import JSONResponse

from backend.app.app_def import (
    API_VERSION,
    DB_COLLECTION_TM_PRJ,
    DB_COLLECTION_TM_TC,
    DB_COLLECTION_TM_TE,
    DB_COLLECTION_TM_TCY,
    DB_NAME_TM
)
from backend.app.cache import (
    cache_get,
    cache_set,
    cache_invalidate,
    cache_invalidate_prefix
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

DB_NAME_TM = DB_NAME_TM.name
DB_COLLECTION_TM_PRJ = DB_COLLECTION_TM_PRJ.name
DB_COLLECTION_TM_TC = DB_COLLECTION_TM_TC.name
DB_COLLECTION_TM_TE = DB_COLLECTION_TM_TE.name
DB_COLLECTION_TM_TCY = DB_COLLECTION_TM_TCY.name


@router.get(f"/api/{API_VERSION}/tm/projects",
            tags=[DB_COLLECTION_TM_PRJ],
            response_model=list[Project],
            status_code=status.HTTP_200_OK)
async def get_all_projects(request: Request):
    """Endpoint to get projects"""

    cached = cache_get("projects:all")
    if cached is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=cached)

    db = request.app.state.mdb

    # Retrieve all projects from database
    projects = await db.find(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {})

    # Concurrently fetch test case and cycle counts for all projects
    async def fetch_counts(project):
        tc_count, tcy_count = await asyncio.gather(
            db.count(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project["project_key"]}),
            db.count(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"project_key": project["project_key"]})
        )
        project["test_case_count"] = tc_count
        project["test_cycle_count"] = tcy_count
        return project

    projects = list(await asyncio.gather(*[fetch_counts(p) for p in projects]))

    cache_set("projects:all", projects)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=projects)


@router.post(f"/api/{API_VERSION}/tm/projects",
             tags=[DB_COLLECTION_TM_PRJ],
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
            content={"error": f"Duplicated labels in request"}
        )

    # Check project exists with direct find_one (no need for counts)
    existing = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {
        "project_key": project_key
    })
    if existing is not None:
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
    await db.create(DB_NAME_TM, DB_COLLECTION_TM_PRJ, db_insert)

    # Invalidate project list cache so next GET sees the new project
    cache_invalidate("projects:all")

    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=request_data)


@router.get(f"/api/{API_VERSION}/tm/projects/{{project_key}}",
            tags=[DB_COLLECTION_TM_PRJ],
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def get_project_by_key(request: Request,
                             project_key: str):
    """Endpoint to get project"""

    cache_key = f"projects:{project_key}"
    cached = cache_get(cache_key)
    if cached is not None:
        return JSONResponse(status_code=status.HTTP_200_OK, content=cached)

    db = request.app.state.mdb

    # Concurrently fetch project, test case count, and cycle count
    project, tc_count, tcy_count = await asyncio.gather(
        db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {"project_key": project_key}),
        db.count(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project_key}),
        db.count(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"project_key": project_key})
    )

    if project is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Assign counts to project
    project["test_case_count"] = tc_count
    project["test_cycle_count"] = tcy_count

    cache_set(cache_key, project)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=project)


@router.put(f"/api/{API_VERSION}/tm/projects/{{project_key}}",
            tags=[DB_COLLECTION_TM_PRJ],
            response_model=Project,
            status_code=status.HTTP_200_OK)
async def update_project_by_key(request: Request,
                                project_key: str,
                                project_update: ProjectUpdate):
    """Endpoint to update project"""

    db = request.app.state.mdb

    # Check project exists with direct find_one
    existing = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {
        "project_key": project_key
    })
    if existing is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

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

    # Concurrently fetch test case and cycle counts
    tc_count, tcy_count = await asyncio.gather(
        db.count(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project_key}),
        db.count(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"project_key": project_key})
    )

    request_data["test_case_count"] = tc_count
    request_data["test_cycle_count"] = tcy_count

    # Update project in DB then fetch updated doc concurrently
    await db.update(DB_NAME_TM, DB_COLLECTION_TM_PRJ, request_data, {
        "project_key": project_key
    })

    updated_project = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {
        "project_key": project_key
    })

    # Invalidate stale cached entries for this project
    cache_invalidate("projects:all", f"projects:{project_key}")

    return JSONResponse(status_code=status.HTTP_200_OK,
                        content=updated_project)


@router.delete(f"/api/{API_VERSION}/tm/projects/{{project_key}}",
               tags=[DB_COLLECTION_TM_PRJ],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_by_key(request: Request,
                                project_key: str,
                                force: dict = None):
    """Endpoint to delete project"""

    db = request.app.state.mdb

    # Check project exists with direct find_one
    existing = await db.find_one(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {
        "project_key": project_key
    })
    if existing is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"{project_key} not found"}
        )

    # Check force flag
    if force and force.get("force", None) is False:
        # Concurrently count all linked collections
        tc_count, te_count, tcy_count = await asyncio.gather(
            db.count(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project_key}),
            db.count(DB_NAME_TM, DB_COLLECTION_TM_TE, {"project_key": project_key}),
            db.count(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"project_key": project_key})
        )
        if tc_count > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Project {project_key} contains linked test-cases"}
            )
        if te_count > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Project {project_key} contains linked test-executions"}
            )
        if tcy_count > 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Project {project_key} contains linked test-cycles"}
            )

    else:
        # Concurrently force delete all linked collections
        await asyncio.gather(
            db.delete(DB_NAME_TM, DB_COLLECTION_TM_TCY, {"project_key": project_key}),
            db.delete(DB_NAME_TM, DB_COLLECTION_TM_TE, {"project_key": project_key}),
            db.delete(DB_NAME_TM, DB_COLLECTION_TM_TC, {"project_key": project_key})
        )

    # Delete the project from the database
    await db.delete(DB_NAME_TM, DB_COLLECTION_TM_PRJ, {
        "project_key": project_key
    })

    # Invalidate all project-related cache entries
    cache_invalidate("projects:all", f"projects:{project_key}")
    cache_invalidate_prefix(f"test_cases:{project_key}")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
