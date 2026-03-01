# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging
import random
import uuid

import pytest
import requests

from .test_base import OrbitTMBaseTest


@pytest.mark.order(5)
class TestOrbitTMGenerate(OrbitTMBaseTest):

    def test_generate_mock_data(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Generate project
        projects = 1
        cases = 50
        for i in range(1, projects + 1):
            project_key = f"PRJ{i}"
            response = requests.post(f"{self.__class__.url}/tm/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}",
                "labels": ["A", "B", "C"]
            })
            assert response.status_code == 201

            # Generate test cases for project
            execution_list = []
            for j in range(1, cases + 1):
                test_case_key = f"{project_key}-T{j}"
                response = requests.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
                    "test_case_key": test_case_key,
                    "project_key": project_key,
                    "title": f"Test Case #{j} ({project_key}) - {uuid.uuid4()}",
                    "description": f"Description for Test Case #{j} in {project_key} - {uuid.uuid4()}",
                    "status": random.choice(["APPROVED", "DRAFT"]),
                    "test_frequency": [random.choice(["NIGHTLY", "WEEKLY"])],
                    "labels": random.sample(["A", "B", "C"], k=random.randint(1, 3))
                })
                assert response.status_code == 201

                # Generate test executions for test cases
                te_count = 1
                for l in range(1, te_count + 1):
                    response = requests.post(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{test_case_key}/executions", json={
                        "result": random.choice(["PASS", "FAIL", "BLOCKED", "NOT_EXECUTED"]),
                        "comments": f"Execution {l} for {test_case_key} - {uuid.uuid4()}"
                    })
                    assert response.status_code == 201
                    execution_list.append(response.json().get("execution_key"))

                # Check test executions created for test case
                response = requests.get(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{test_case_key}/executions")
                assert response.status_code == 200
                assert len(response.json()) == te_count

            # Create cycles
            cycles = 1
            for j in range(1, cycles + 1):
                response = requests.post(f"{self.__class__.url}/tm/projects/{project_key}/cycles", json={
                    "title": f"Cycle #{j} ({project_key}) - {uuid.uuid4()}"
                })
                assert response.status_code == 201
                cycle_key = response.json().get("test_cycle_key")

                for ii in range(1, len(execution_list) + 1):
                    # Add execution to cycle
                    execution = execution_list.pop()
                    response = requests.post(f"{self.__class__.url}/tm/cycles/{cycle_key}/executions", params={
                        "execution_key": execution,
                        "custom_field_values": {
                            "custom_field_1": f"Value {ii} for {execution}",
                            "custom_field_2": f"Value {ii} for {execution}"
                        }
                    })
                    assert response.status_code == 200

        logging.info(f"--- Test: {request.node.name} Complete ---")
