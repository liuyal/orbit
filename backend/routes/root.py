# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# routes/root.py

import json
import logging
import tempfile
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

    def iterfile():
        """ Helper function to iterate through all db items """

        try:
            while True:
                chunk = tmp_file.read(1024 * 1024)
                if not chunk:
                    break

                yield chunk

        finally:
            tmp_file.close()

    db = request.app.state.mdb

    # Select the database
    db_target_list = db_selection(db_name)

    # Spill to disk once the export exceeds ~50MB
    max_size = 25 * 1024 * 1024
    tmp_file = tempfile.SpooledTemporaryFile(max_size=max_size)

    with zipfile.ZipFile(tmp_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for db_item in db_target_list:
            collection_names = await db.list_collections(db_name=db_item.name)
            for collection_name in collection_names:

                with zf.open(f"{db_item.name}/{collection_name}.json",
                             mode="w",
                             force_zip64=True) as entry:

                    entry.write(b"[")
                    first = True

                    async for doc in db.export_collection_stream(
                            db_name=db_item.name,
                            collection_name=collection_name
                    ):
                        if not first:
                            entry.write(b",")

                        first = False
                        entry.write(b"\n")
                        entry.write(json.dumps(doc, indent=2).encode("utf-8"))

                    entry.write(b"\n]")

    tmp_file.seek(0)

    return StreamingResponse(
        iterfile(),
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
