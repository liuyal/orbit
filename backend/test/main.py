# ================================================================
# Orbit API
# Description: FastAPI backend sanity test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import unittest

from test_cases import OrbitTMTestCasesTest
from test_cycles import OrbitTMCyclesTest
from test_executions import OrbitTMExecutionsTest
from test_projects import OrbitTMProjectsTest

if __name__ == "__main__":
    project_tests = OrbitTMProjectsTest()
    test_cases_tests = OrbitTMTestCasesTest()
    test_executions_test = OrbitTMExecutionsTest()
    test_cycles_test = OrbitTMCyclesTest()

    unittest.TestSuite([
        project_tests,
        test_cases_tests,
        test_executions_test,
        test_cycles_test
    ])

    unittest.main()
