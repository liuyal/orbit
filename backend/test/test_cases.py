# ================================================================
# Orbit API
# Description: FastAPI backend sanity test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging
import unittest

import pytest

from test_base import OrbitTMBaseTest


class OrbitTMTestCasesTest(OrbitTMBaseTest):

    @pytest.mark.order(1)
    def test_get_all_test_cases(self):
        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        # n = 3
        # k = 10
        # for i in range(0, n):
        #     project_key = f"PRJ{i}"
        #     payload = {"project_key": project_key, "description": f"Project #{i}"}
        #
        #     response = requests.post(f"{self.__class__.url}/projects", json=payload)
        #     assert response.status_code == 201
        #
        #     response = requests.get(f"{self.__class__.url}/projects")
        #     assert response.status_code == 200
        #     assert len(response.json()) == i + 1
        #
        #     for j in range(0, k):
        #         ti = j + i * k
        #         payload = {"test_case_key": f"{project_key}-T{ti}", "project_key": project_key}
        #         response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json=payload)
        #         assert response.status_code == 201
        #
        #         response = requests.get(f"{self.__class__.url}/test-cases")
        #         assert response.status_code == 200
        #         assert len(response.json()) == (j + i * k) + 1
        #
        # response = requests.get(f"{self.__class__.url}/test-cases")
        # assert response.status_code == 200
        # assert len(response.json()) == n * k
        #
        # for i in range(0, n):
        #     for j in range(0, k):
        #         ti = j + i * k
        #         project_key = f"PRJ{i}"
        #         test_case_key = f"{project_key}-T{ti}"
        #         response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}")
        #         assert response.status_code == 200
        #
        #         title_updated = f"Test Case title {project_key}-T{ti} ++++"
        #         response = requests.put(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}", json={"title": title_updated})
        #         assert response.status_code == 200
        #
        #         response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}")
        #         assert response.status_code == 200
        #         assert response.json()["title"] == title_updated
        #
        # prj_key = "PRJ0"
        # response = requests.delete(f"{self.__class__.url}/projects/{prj_key}/test-cases/")
        # assert response.status_code == 204
        #
        # response = requests.get(f"{self.__class__.url}/test-cases")
        # assert response.status_code == 200
        # assert len(response.json()) == n * k - k

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")


if __name__ == "__main__":
    unittest.main()
