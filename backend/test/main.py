# ================================================================
# Orbit API
# Description: FastAPI backend sanity test script for the Orbit application.
# Version: 0.1.0
# Author: Jerry
# License: MIT
# ================================================================

import unittest

from test_projects import OrbitBackendProjectsTest

# from test_cases import OrbitBackendTestCasesTest
# from test_executions import OrbitBackendExecutionsTest
# from test_cycles import OrbitBackendCyclesTest


if __name__ == "__main__":
    project_tests = OrbitBackendProjectsTest
    # test_cases_tests = OrbitBackendTestCasesTest
    # executions_test = OrbitBackendExecutionsTest
    # cycles_test = OrbitBackendCyclesTest

    unittest.main()
