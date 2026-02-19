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

        # Generate project
        projects = 2
        cases = 20
        for i in range(1, projects + 1):
            project_key = f"PRJ{i}"
            response = requests.post(f"{self.__class__.url}/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}",
                "labels": ["A", "B", "C"]
            })
            assert response.status_code == 201

            # Generate test cases for project
            execution_list = []
            for j in range(1, cases + 1):
                test_case_key = f"{project_key}-T{j}"
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-case", json={
                    "test_case_key": test_case_key,
                    "project_key": project_key,
                    "title": f"Test Case #{j} ({project_key})"
                })
                assert response.status_code == 201

                # Generate test executions for test cases
                te_count = 20
                for l in range(1, te_count + 1):
                    response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
                    assert response.status_code == 201
                    if l == 3:
                        execution_list.append(response.json().get("execution_key"))

                # Check test executions created for test case
                response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
                assert response.status_code == 200
                assert len(response.json()) == te_count

            # Create cycles
            cycles = 3
            for j in range(1, cycles + 1):
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/cycles")
                assert response.status_code == 201
                cycle_key = response.json().get("test_cycle_key")

                for i in range(1, 5 + 1):
                    # Add execution to cycle
                    last_execution = execution_list.pop()
                    response = requests.post(f"{self.__class__.url}/cycles/{cycle_key}/executions", params={
                        "execution_key": last_execution
                    })
                    assert response.status_code == 200

        logging.info(f"--- Test: {request.node.name} Complete ---")
