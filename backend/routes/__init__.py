from .projects import router as projects_router
from .test_cases import router as test_cases_router
from .executions import router as executions_router
from .cycles import router as cycles_router

routers = [projects_router, test_cases_router, executions_router, cycles_router]

