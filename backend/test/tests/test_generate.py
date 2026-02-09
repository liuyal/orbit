# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging

import pytest
import requests

from .test_base import OrbitTMBaseTest


@pytest.mark.order(5)
class TestOrbitTMGenerate(OrbitTMBaseTest):

    def test_generate_mock_data(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Generate 25 project
        projects = 10
        cases = 50
        for i in range(1, projects + 1):
            project_key = f"PRJ{i}"
            response = requests.post(f"{self.__class__.url}/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}"
            })
            assert response.status_code == 201

            # Generate test cases for project
            for j in range(1, cases + 1):
                test_case_key = f"{project_key}-T{j}"
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json={
                    "test_case_key": test_case_key,
                    "project_key": project_key,
                    "title": f"Test Case #{j}"
                })
                assert response.status_code == 201

                # Generate test executions for test cases
                te_count = 10
                for l in range(1, te_count + 1):
                    response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
                    assert response.status_code == 201

                # Check test executions created for test case
                response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
                assert response.status_code == 200
                assert len(response.json()) == te_count

            # Create cycle & Check cycle created
            cycles = 10
            for j in range(1, cycles + 1):
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/cycles")
                assert response.status_code == 201

            # Add executions to cycles
            for j in range(1, cycles + 1):
                cycle_key = f"{project_key}-C{j}"

                # for i in range(1, te_count * tc_count):
                #     execution_key = f"{project_key}-E{i}"
                #     response = requests.post(f"{self.__class__.url}/cycles/{cycle_key}/executions?execution_key={execution_key}")
                #     assert response.status_code == 200


        logging.info(f"--- Test: {request.node.name} Complete ---")
