# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Version: 0.1.0
# Author: Jerry
# License: MIT
# ================================================================

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from db import get_client, DB_NAME
from routes import routers


@asynccontextmanager
async def lifespan(app):
    client = get_client()
    app.state.db = client[DB_NAME]
    yield
    client.close()


app = FastAPI(title="ORBIT",
              description="API spec for Orbit application",
              version="0.1.0",
              debug=True,
              lifespan=lifespan
              )


@app.get("/", tags=["root"])
async def root(request: Request):
    """ Root endpoint to check service status. """

    # TODO add service status info
    return RedirectResponse(url="/docs")


for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5080)
