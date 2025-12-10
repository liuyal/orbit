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

        logging.info(f"Initialize Tests...")

        cls.host = pytest.options['host']
        cls.port = pytest.options['port']
        cls.protocol = pytest.options['protocol']
        cls.url = f"{cls.protocol}://{cls.host}:{cls.port}/tm/api/v1"

    @classmethod
    def tearDownClass(cls):
        """ Teardown device """

        logging.info(f"Teardown Tests...")

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

        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert response.json() == []

        n = 3
        for i in range(0, n):
            payload = {"project_key": f"PRJ{i}", "description": f"Project #{i}"}
            response = requests.post(f"{self.__class__.url}/projects", json=payload)
            assert response.status_code == 201

        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == n

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(2)
    def test_test_cases(self):
        """ Test: Test Cases """

        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        n = 3
        for i in range(0, n):
            payload = {"project_key": f"PRJ{i}", "description": f"Project #{i}"}
            response = requests.post(f"{self.__class__.url}/projects", json=payload)
            assert response.status_code == 201
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == n

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

        project_key = "PRJ2"
        for i in range(0, n):
            payload = {"test_case_key": f"{project_key}-T{i}", "project_key": project_key}
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json=payload)
            assert response.status_code == 201
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n * 3

        prj_key = "PRJ1"
        response = requests.delete(f"{self.__class__.url}/projects/{prj_key}/test-cases/")
        assert response.status_code == 204
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n * 2

        prj_key = "PRJ2"
        response = requests.delete(f"{self.__class__.url}/projects/{prj_key}/test-cases/")
        assert response.status_code == 204
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == n

        prj_key = "PRJ0"
        response = requests.delete(f"{self.__class__.url}/projects/{prj_key}/test-cases/")
        assert response.status_code == 204
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(3)
    def test_test_executions(self):
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
        print(response.content)
        assert response.status_code == 200
        assert len(response.json()) == n

        # self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")


if __name__ == "__main__":
    unittest.main()
