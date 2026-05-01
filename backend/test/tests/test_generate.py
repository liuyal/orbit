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

from .test_base import OrbitTMBaseTest

PROJECT_COUNT = 1
TEST_CASES_COUNT = 50
TEST_CYCLES_COUNT = 20


@pytest.mark.order(5)
class TestOrbitTMGenerate(OrbitTMBaseTest):

    def test_generate_mock_data(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Generate project
        projects = PROJECT_COUNT
        cases = TEST_CASES_COUNT
        session = self.__class__.session
        for i in range(1, projects + 1):
            project_key = f"PRJ{i}"
            response = session.post(f"{self.__class__.url}/tm/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}",
                "labels": ["A", "B", "C"]
            })
            assert response.status_code == 201

            # Generate test cases for project
            test_cases = []
            for j in range(1, cases + 1):
                test_case_key = f"{project_key}-T{j}"
                response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
                    "test_case_key": test_case_key,
                    "project_key": project_key,
                    "title": f"Test Case #{j} ({project_key}) - {uuid.uuid4()}",
                    "description": f"Description for Test Case #{j} in {project_key} - {uuid.uuid4()}",
                    "status": random.choice(["APPROVED", "DRAFT", "EXPECTED FAIL"]),
                    "test_frequency": random.sample(["NIGHTLY", "WEEKLY"], k=random.randint(1, 2)),
                    "labels": random.sample(["A", "B", "C", "D"], k=random.randint(1, 3))
                })
                assert response.status_code == 201
                test_cases.append(test_case_key)

            # Create cycles
            cycles = TEST_CYCLES_COUNT
            for j in range(1, cycles + 1):
                response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/cycles", json={
                    "title": f"Cycle #{j} ({project_key}) - {uuid.uuid4()}"
                })
                assert response.status_code == 201
                cycle_key = response.json().get("test_cycle_key")

                # Randomly select result sets for executions
                result_set_1 = ["PASS", "FAIL", "BLOCKED", "NOT_EXECUTED"]
                result_set_2 = ["PASS", "FAIL", "BLOCKED"]
                result_set_3 = ["NOT_EXECUTED"]
                result_set = random.choices([result_set_1, result_set_2, result_set_3], weights=[10, 10, 4], k=1)[0]

                # Generate test executions for test cases
                for l in range(1, len(test_cases) + 1):
                    test_case_key = test_cases[l - 1]
                    response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{test_case_key}/executions", json={
                        "result": random.choice(result_set),
                        "comments": f"Execution {l} for {test_case_key} - {uuid.uuid4()}"
                    })
                    assert response.status_code == 201

                    # Add to cycle
                    execution = response.json().get("execution_key")
                    response = session.post(f"{self.__class__.url}/tm/cycles/{cycle_key}/executions", params={
                        "execution_key": execution,
                        "custom_field_values": {
                            "custom_field_1": f"Value {l} for {execution}",
                            "custom_field_2": f"Value {l * 2} for {execution}"
                        }
                    })
                    assert response.status_code == 200

        logging.info(f"--- Test: {request.node.name} Complete ---")
