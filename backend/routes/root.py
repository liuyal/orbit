# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/root.py

import io
import json
import logging
import zipfile

from fastapi import (
    APIRouter,
    Request,
    status,
    Response
)
from fastapi.responses import (
    RedirectResponse,
    StreamingResponse
)
from starlette.responses import JSONResponse

from backend.app.app_def import (
    API_VERSION,
    DBTarget,
    DB_ALL,
    DB_NAME_TM,
    DB_NAME_RUNNERS,
    DB_RESET_TOKEN
)
from backend.app.cache import cache_invalidate_prefix

router = APIRouter()

logger = logging.getLogger(__name__)


def db_selection(db_name: DBTarget):
    """ Helper function to select the database based on the db_name parameter. """

    if db_name == DBTarget.TM:
        return [DB_NAME_TM]

    elif db_name == DBTarget.RUNNERS:
        return [DB_NAME_RUNNERS]

    elif db_name == DBTarget.ALL:
        return DB_ALL

    else:
        raise ValueError(f"Invalid db_target value: {db_name}")


@router.get(f"/", tags=["root"])
async def root(request: Request):
    """ Root endpoint to check service status. """

    logger.info(f"ROOT ENDPOINT")
    logger.debug("ROOT ENDPOINT DEBUG")

    # TODO add service status info
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(f"/api/{API_VERSION}",
            tags=["root"])
async def root_api(request: Request):
    """ Root api endpoint to check service status. """

    logger.debug(f"/api/{API_VERSION} path redirecting to docs pages")
    base_url = f"{request.url.scheme}://{request.url.netloc}"

    return RedirectResponse(url=f"{base_url}/api/{API_VERSION}/docs")


@router.get(f"/api/{API_VERSION}/db-export",
            tags=["root"])
async def get_database_export(request: Request,
                              db_name: DBTarget):
    """ Root api endpoint to get a dump of the database. """

    db = request.app.state.mdb

    # Select the database
    db_target_list = db_selection(db_name)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for db_item in db_target_list:
            # Call the export database function
            export_data = await db.export(db_name=db_item.name)
            # Write the exported data to the zip file as JSON
            for collection_name, documents in export_data.items():
                json_bytes = json.dumps(documents, indent=2).encode("utf-8")
                zf.writestr(f"{db_item.name}/{collection_name}.json", json_bytes)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        status_code=status.HTTP_200_OK,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="db-export-{db_name.value}.zip"'}
    )


@router.post(f"/api/{API_VERSION}/db-reset",
             tags=["root"],
             status_code=status.HTTP_204_NO_CONTENT)
async def reset_database(request: Request,
                         db_name: DBTarget,
                         db_reset_token: str):
    """ Root endpoint to reset server database. """

    if db_reset_token != DB_RESET_TOKEN:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": f"Invalid token for db reset"})

    db = request.app.state.mdb

    # Select the database
    db_target_list = db_selection(db_name)

    # Call the configure function with the clean_db parameter to reset the database
    await db.configure(clean_db=db_target_list)

    # Clear all in-memory caches so stale data is never served after a reset
    cache_invalidate_prefix()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
