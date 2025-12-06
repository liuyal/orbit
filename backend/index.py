import uvicorn
from fastapi import FastAPI

from routes import routers

app = FastAPI(title="Orbit API",
              description="API spec for Orbit application",
              version="0.1.0",
              debug=True)

# @app.get("/")
# def root():
#     """ Root endpoint to check service status. """
#
#     return {"message": "Service is up and running!"}


for router in routers:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
