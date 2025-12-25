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


class OrbitBackendSanityTest(unittest.TestCase):
    """ Orbit Sanity Tests """

    @classmethod
    def setUpClass(cls):
        """ Initialize device """

        logging.info(f"Initialize tests...")

        # Get test parameters
        cls.host = pytest.options['host']
        cls.port = pytest.options['port']
        cls.protocol = pytest.options['protocol']
        cls.url = f"{cls.protocol}://{cls.host}:{cls.port}/tm/api/v1"

        # Check if the server is up
        response = requests.get(f"{cls.protocol}://{cls.host}:{cls.port}/")
        assert response.status_code == 200

    @classmethod
    def tearDownClass(cls):
        """ Teardown device """

        logging.info(f"Teardown tests...")
        cls.clean_up_db()

    @classmethod
    def clean_up_db(cls):
        """ Clean up sb after tests """

        # Cleanup existing db
        response = requests.post(f"{cls.url}/reset")
        assert response.status_code == 204

    @pytest.mark.order(1)
    def test_projects(self):
        """ Test: Projects """

        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        # Verify no projects exist after cleanup
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create n projects & verify
        n = 3
        for i in range(0, n):
            # Create project
            payload = {"project_key": f"PRJ{i}", "description": f"Project #{i}"}
            response = requests.post(f"{self.__class__.url}/projects", json=payload)
            assert response.status_code == 201

            # Verify project created
            response = requests.get(f"{self.__class__.url}/projects/PRJ{i}")
            assert response.status_code == 200
            assert response.json()["description"] == f"Project #{i}"
            assert response.json()["is_active"] == True

            # update project description field
            payload = {"description": f"Project #{i} ++++"}
            response = requests.put(f"{self.__class__.url}/projects/PRJ{i}", json=payload)
            assert response.status_code == 200

            # Verify project updated
            response = requests.get(f"{self.__class__.url}/projects/PRJ{i}")
            assert response.status_code == 200
            assert response.json()["description"] == f"Project #{i} ++++"

        # Confirm n projects were created
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == n

        for i in range(0, n):
            # Delete project
            response = requests.delete(f"{self.__class__.url}/projects/PRJ{i}")
            assert response.status_code == 204

            # Verify project deleted
            response = requests.get(f"{self.__class__.url}/projects")
            assert response.status_code == 200
            assert len(response.json()) == n - (i + 1)

        # Verify no projects exist after cleanup
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(2)
    def test_cases(self):
        """ Test: Test Cases """

        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        n = 3
        k = 10
        for i in range(0, n):
            # Create project
            project_key = f"PRJ{i}"
            payload = {"project_key": project_key, "description": f"Project #{i}"}
            response = requests.post(f"{self.__class__.url}/projects", json=payload)
            assert response.status_code == 201

            # Verify projects created
            response = requests.get(f"{self.__class__.url}/projects")
            assert response.status_code == 200
            assert len(response.json()) == i + 1

            for j in range(0, k):
                # Create test case
                ti = j + i * k
                payload = {"test_case_key": f"{project_key}-T{ti}", "project_key": project_key}
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json=payload)
                assert response.status_code == 201

                # Verify test case created
                response = requests.get(f"{self.__class__.url}/test-cases")
                assert response.status_code == 200
                assert len(response.json()) == (j + i * k) + 1

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n * k

        for i in range(0, n):
            for j in range(0, k):
                # Get test case by key
                ti = j + i * k
                project_key = f"PRJ{i}"
                test_case_key = f"{project_key}-T{ti}"
                response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}")
                assert response.status_code == 200

                # Upgrade test case
                title_updated = f"Test Case title {project_key}-T{ti} ++++"
                response = requests.put(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}",
                                        json={"title": title_updated})
                assert response.status_code == 200

                # Verify test case updated
                response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}")
                assert response.status_code == 200
                assert response.json()["title"] == title_updated

                # TODO: add delete test

        # Delete all test cases for project PRJ0
        prj_key = "PRJ0"
        response = requests.delete(f"{self.__class__.url}/projects/{prj_key}/test-cases/")
        assert response.status_code == 204

        # Verify test cases deleted
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n * k - k

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(3)
    def test_executions(self):
        """ Test: Executions """

        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        n = 2
        for i in range(0, n):
            payload = {"project_key": f"PRJ{i}", "description": f"Project #{i}"}
            response = requests.post(f"{self.__class__.url}/projects", json=payload)
            assert response.status_code == 201
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 2

        n = 25
        project_key = "PRJ0"
        for i in range(0, n):
            payload = {"test_case_key": f"{project_key}-T{i}", "project_key": project_key}
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json=payload)
            assert response.status_code == 201
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n

        project_key = "PRJ1"
        for i in range(0, n):
            payload = {"test_case_key": f"{project_key}-T{i}", "project_key": project_key}
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json=payload)
            assert response.status_code == 201
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n * 2

        n = 5
        project_key = "PRJ0"
        test_case_key = f"{project_key}-T0"
        for i in range(0, n):
            payload = {"execution_key": f"{project_key}-E{i}"}
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions", json=payload)
            assert response.status_code == 201
        response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
        assert response.status_code == 200
        assert len(response.json()) == n

        n = 5
        project_key = "PRJ0"
        test_case_key = f"{project_key}-T1"
        for i in range(n, n * 2):
            payload = {"execution_key": f"{project_key}-E{i}"}
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions", json=payload)
            assert response.status_code == 201
        response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
        assert response.status_code == 200
        assert len(response.json()) == n

        # self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    # @pytest.mark.order(4)
    # def test_cycles(self):
    #     """ Test: Cycle """
    #
    #     logging.info(f"--- Starting test: {self._testMethodName} ---")
    #     self.__class__.clean_up_db()
    #
    #     n = 1
    #     for i in range(0, n):
    #         payload = {"project_key": f"PRJ{i}", "description": f"Project #{i}"}
    #         response = requests.post(f"{self.__class__.url}/projects", json=payload)
    #         assert response.status_code == 201
    #     response = requests.get(f"{self.__class__.url}/projects")
    #     assert response.status_code == 200
    #     assert len(response.json()) == n
    #
    #     n = 10
    #     project_key = "PRJ0"
    #     for i in range(0, n):
    #         payload = {"test_case_key": f"{project_key}-T{i}", "project_key": project_key}
    #         response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json=payload)
    #         assert response.status_code == 201
    #     response = requests.get(f"{self.__class__.url}/test-cases")
    #     assert response.status_code == 200
    #     assert len(response.json()) == n
    #
    #     n = 5
    #     project_key = "PRJ0"
    #     test_case_key = f"{project_key}-T1"
    #     for i in range(0, n):
    #         payload = {"execution_key": f"{project_key}-E{i}"}
    #         response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions", json=payload)
    #         assert response.status_code == 201
    #     response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
    #     assert response.status_code == 200
    #     assert len(response.json()) == n
    #
    #     n = 5
    #     project_key = "PRJ0"
    #     test_case_key = f"{project_key}-T2"
    #     for i in range(n, n * 2):
    #         payload = {"execution_key": f"{project_key}-E{i}"}
    #         response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions", json=payload)
    #         assert response.status_code == 201
    #     response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
    #     assert response.status_code == 200
    #     assert len(response.json()) == n
    #
    #     n = 5
    #     project_key = "PRJ0"
    #     test_case_key = f"{project_key}-T3"
    #     for i in range(n * 2, n * 3):
    #         payload = {"execution_key": f"{project_key}-E{i}"}
    #         response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions", json=payload)
    #         assert response.status_code == 201
    #     response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
    #     assert response.status_code == 200
    #     assert len(response.json()) == n
    #
    #     # self.__class__.clean_up_db()
    #     logging.info(f"--- Test: {self._testMethodName} Complete ---")


if __name__ == "__main__":
    unittest.main()
