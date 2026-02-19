# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging

import pytest

from .test_base import OrbitTMBaseTest


@pytest.mark.order(3)
class TestOrbitTMExecutions(OrbitTMBaseTest):

    def test_get_all_executions_by_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # n = 2
        # for i in range(0, n):
        #     payload = {"project_key": f"PRJ{i}", "description": f"Project #{i}"}
        #     response = requests.post(f"{self.__class__.url}/projects", json=payload)
        #     assert response.status_code == 201
        #
        # response = requests.get(f"{self.__class__.url}/projects")
        # assert response.status_code == 200
        # assert len(response.json()) == 2
        #
        # n = 25
        # project_key = "PRJ0"
        # for i in range(0, n):
        #     payload = {"test_case_key": f"{project_key}-T{i}", "project_key": project_key}
        #     response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-case", json=payload)
        #     assert response.status_code == 201
        #
        # response = requests.get(f"{self.__class__.url}/test-cases")
        # assert response.status_code == 200
        # assert len(response.json()) == n
        #
        # project_key = "PRJ1"
        # for i in range(0, n):
        #     payload = {"test_case_key": f"{project_key}-T{i}", "project_key": project_key}
        #     response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-case", json=payload)
        #     assert response.status_code == 201
        #
        # response = requests.get(f"{self.__class__.url}/test-cases")
        # assert response.status_code == 200
        # assert len(response.json()) == n * 2
        #
        # n = 5
        # project_key = "PRJ0"
        # test_case_key = f"{project_key}-T0"
        # for i in range(0, n):
        #     payload = {"execution_key": f"{project_key}-E{i}"}
        #     response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions", json=payload)
        #     assert response.status_code == 201
        #
        # response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
        # assert response.status_code == 200
        # assert len(response.json()) == n
        #
        # n = 5
        # project_key = "PRJ0"
        # test_case_key = f"{project_key}-T1"
        # for i in range(n, n * 2):
        #     payload = {"execution_key": f"{project_key}-E{i}"}
        #     response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions", json=payload)
        #     assert response.status_code == 201
        #
        # response = requests.get(f"{self.__class__.url}/projects/{project_key}/test-cases/{test_case_key}/executions")
        # assert response.status_code == 200
        # assert len(response.json()) == n

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_all_executions_by_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_all_executions_by_test_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_executions_by_test_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_all_executions_by_test_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_executions_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_executions_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_executions_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")
