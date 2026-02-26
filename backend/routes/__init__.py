# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

from .projects import router as projects_router
from .root import router as root_router
from .test_cases import router as test_cases_router
from .test_cycles import router as cycles_router
from .test_executions import router as executions_router
from .runners import router as runners_router

routers = [root_router,
           projects_router,
           test_cases_router,
           executions_router,
           cycles_router,
           runners_router]
