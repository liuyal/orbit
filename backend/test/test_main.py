# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

from tests.test_cases import TestOrbitTMCases
from tests.test_cycles import TestOrbitTMCycles
from tests.test_executions import TestOrbitTMExecutions
from tests.test_generate import TestOrbitTMGenerate
from tests.test_projects import TestOrbitTMProjects

if __name__ == '__main__':
    project_tests = TestOrbitTMProjects()
    cases_test = TestOrbitTMCases()
    execution_tests = TestOrbitTMExecutions()
    cycle_tests = TestOrbitTMCycles()
    generate_tests = TestOrbitTMGenerate()
