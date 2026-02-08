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


@pytest.mark.order(2)
class TestOrbitTMCases(OrbitTMBaseTest):

    def test_get_all_test_cases(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create multiple projects and test cases
        projects = 2
        cases = 20
        count = 0

        # Create projects and test cases
        for i in range(1, projects + 1):
            # Create Test cases for non-existent project (should fail)
            project_key = f"PRJ{i}"
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases")
            assert response.status_code == 404

            # Create project
            response = requests.post(f"{self.__class__.url}/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}"
            })
            assert response.status_code == 201

            # Create test cases for the project
            for j in range(1, cases + 1):
                count += 1
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json={
                    "test_case_key": f"{project_key}-T{j}",
                    "project_key": project_key,
                    "title": f"Test Case {j} for {project_key}",
                    "description": f"Description for Test Case {j} in {project_key}",
                    "folder": f"/",
                    "status": "APPROVED",
                    "priority": "NORMAL",
                    "test_script": f"x = {count};",
                    "test_frequency": ["NIGHTLY"],
                    "labels": ["A", "B"],
                    "links": [f"http://example.com/test-case/{project_key}-T{j}"]
                })
                assert response.status_code == 201, response.json()
                assert response.json()["test_case_key"] == f"{project_key}-T{j}"
                assert response.json()["project_key"] == project_key
                assert response.json()["title"] == f"Test Case {j} for {project_key}"
                assert response.json()["description"] == f"Description for Test Case {j} in {project_key}"
                assert response.json()["folder"] == f"/"
                assert response.json()["status"] == "APPROVED"
                assert response.json()["priority"] == "NORMAL"
                assert response.json()["test_script"] == f"x = {count};"
                assert response.json()["test_frequency"] == ["NIGHTLY"]
                assert response.json()["labels"] == ["A", "B"]
                assert response.json()["links"] == [f"http://example.com/test-case/{project_key}-T{j}"]

                # Check test cases count after each addition
                response = requests.get(f"{self.__class__.url}/test-cases")
                assert response.status_code == 200
                assert len(response.json()) == count

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert count == projects * cases
        assert len(response.json()) == projects * cases

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_all_test_cases_by_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create multiple projects and test cases
        projects = 5
        cases = 10
        count = 0

        # Create projects and test cases
        for i in range(1, projects + 1):
            # Create Test cases for non-existent project (should fail)
            project_key = f"PRJ{i}"
            response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases")
            assert response.status_code == 404

            # Create project
            response = requests.post(f"{self.__class__.url}/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}"
            })
            assert response.status_code == 201

            # Create test cases for the project
            for j in range(1, cases + 1):
                count += 1
                response = requests.post(f"{self.__class__.url}/projects/{project_key}/test-cases", json={
                    "test_case_key": f"{project_key}-T{j}",
                    "project_key": project_key
                })
                assert response.status_code == 201

                # Check test cases count after each addition
                response = requests.get(f"{self.__class__.url}/test-cases")
                assert response.status_code == 200
                assert len(response.json()) == count

        for i in range(1, projects + 1):
            # Get test cases for each project and verify count
            response = requests.get(f"{self.__class__.url}/projects/PRJ{i}/test-cases")
            assert response.status_code == 200
            assert len(response.json()) == cases

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_test_case_in_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_all_test_cases_by_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_test_cases_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_test_cases_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_test_cases_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        # Check total test cases
        response = requests.get(f"{self.__class__.url}/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")
