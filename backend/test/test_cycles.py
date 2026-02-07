# ================================================================
# Orbit API
# Description: FastAPI backend sanity test script for the Orbit application.
# Version: 0.1.0
# Author: Jerry
# License: MIT
# ================================================================

import logging
import unittest

import pytest
import requests

from test_base import OrbitBackendBaseTest


class OrbitBackendCyclesTest(OrbitBackendBaseTest):

    @pytest.mark.order(1)
    def test_cycles(self):
        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        n = 50
        for i in range(0, n):
            payload = {"project_key": f"PRJ{i}", "description": f"Project #{i}"}
            response = requests.post(f"{self.__class__.url}/projects", json=payload)
            assert response.status_code == 201

        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == n

        n = 120
        project_key = "PRJ0"
        for i in range(0, n):
            payload = {"test_case_key": f"{project_key}-T{i}", "project_key": project_key}
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json=payload)
            assert response.status_code == 201

        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n

        te_count = 5
        tc_count = 10
        for j in range(1, tc_count + 1):
            test_case_key = f"{project_key}-T{j}"
            for i in range(1, te_count + 1):
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
                assert response.status_code == 201

            response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
            assert response.status_code == 200
            assert len(response.json()) == te_count

            response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}")
            assert response.status_code == 200
            assert response.json()["last_execution_key"] == f"{project_key}-E{j * te_count}"

        response = requests.get(f"{self.__class__.url}/projects/{project_key}/executions")
        assert response.status_code == 200
        assert len(response.json()) == tc_count * te_count

        response = requests.get(f"{self.__class__.url}/projects/{project_key}/cycles")
        assert response.status_code == 200
        assert len(response.json()) == 0

        for j in range(1, 7):
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/cycles")
            assert response.status_code == 201

        response = requests.get(f"{self.__class__.url}/projects/{project_key}/cycles")
        assert response.status_code == 200
        assert len(response.json()) == 6

        cycle_key = f"{project_key}-C{1}"
        response = requests.get(f"{self.__class__.url}/cycles/{cycle_key}")
        assert response.status_code == 200
        assert response.json()["test_cycle_key"] == cycle_key

        cycle_key = f"{project_key}-C{2}"
        response = requests.get(f"{self.__class__.url}/cycles/{cycle_key}")
        assert response.status_code == 200
        assert response.json()["test_cycle_key"] == cycle_key

        cycle_key = f"{project_key}-C{1}"
        payload = {"title": "CYCLE1"}
        response = requests.put(f"{self.__class__.url}/cycles/{cycle_key}", json=payload)
        assert response.status_code == 200
        assert response.json()["test_cycle_key"] == cycle_key

        response = requests.get(f"{self.__class__.url}/cycles/{cycle_key}")
        assert response.status_code == 200
        assert response.json()["test_cycle_key"] == cycle_key
        assert response.json()["title"] == payload["title"]

        cycle_key = f"{project_key}-C{1}"
        response = requests.get(f"{self.__class__.url}/cycles/{cycle_key}/executions")
        assert response.status_code == 200
        assert len(response.json()) == 0

        for j in range(1, 7):
            cycle_key = f"{project_key}-C{j}"
            for i in range(1, te_count * tc_count):
                execution_key = f"{project_key}-E{i}"
                response = requests.post(f"{self.__class__.url}/cycles/{cycle_key}/executions?execution_key={execution_key}")
                assert response.status_code == 200

            response = requests.get(f"{self.__class__.url}/cycles/{cycle_key}/executions")
            assert response.status_code == 200
            assert len(response.json()) == tc_count

        cycle_key = f"{project_key}-C{6}"
        execution_key = f"{project_key}-E{5}"
        response = requests.delete(f"{self.__class__.url}/cycles/{cycle_key}/executions/{execution_key}")
        assert response.status_code == 200

        response = requests.get(f"{self.__class__.url}/cycles/{cycle_key}/executions")
        assert response.status_code == 200
        assert len(response.json()) == 9
        cycle_key = f"{project_key}-C{6}"

        response = requests.delete(f"{self.__class__.url}/cycles/{cycle_key}")
        assert response.status_code == 204

        response = requests.get(f"{self.__class__.url}/projects/{project_key}/cycles")
        assert response.status_code == 200
        assert len(response.json()) == 5

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")


if __name__ == "__main__":
    unittest.main()
