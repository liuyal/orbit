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


class OrbitBackendProjectsTest(OrbitBackendBaseTest):

    @pytest.mark.order(1)
    def test_get_all_projects(self):
        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        # Check no projects exist
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create projects
        n = 10
        active_list = [False] + [True] * (n - 2) + [False]
        for i in range(0, n):
            response = requests.post(f"{self.__class__.url}/projects", json={
                "project_key": f"PRJ{i}",
                "description": f"Project #{i}",
                "is_active": active_list[i],
                "labels": ["A", "B", "C"]
            })
            assert response.status_code == 201

        # Check project list
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == n

        for i in range(0, n):
            assert response.json()[i]["project_key"] == f"PRJ{i}"
            assert response.json()[i]["description"] == f"Project #{i}"
            assert response.json()[i]["is_active"] == active_list[i]
            assert response.json()[i]["labels"] == ["A", "B", "C"]
            assert response.json()[i]["test_case_count"] == 0
            assert response.json()[i]["test_cycle_count"] == 0

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(2)
    def test_create_project_by_key(self):
        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        # Check no projects
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Check duplicated labels
        response = requests.post(f"{self.__class__.url}/projects", json={
            "project_key": f"PRJ-WDD",
            "description": f"Project #WDD",
            "is_active": True,
            "labels": ["A", "B", "C", "A", "B", "C"]
        })
        assert response.status_code == 400
        assert response.json()["error"] == f"Duplicate labels are not allowed"

        # Check no projects
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Add valid test case
        response = requests.post(f"{self.__class__.url}/projects", json={
            "project_key": f"PRJ-WDD",
            "description": f"Project #WDD",
            "is_active": True,
            "labels": ["A", "B", "C"]
        })
        assert response.status_code == 201

        # Get project details
        response = requests.get(f"{self.__class__.url}/projects/PRJ-WDD")
        assert response.status_code == 200
        assert response.json()["project_key"] == f"PRJ-WDD"
        assert response.json()["description"] == f"Project #WDD"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Check projects is 1
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Add duplicated test case
        response = requests.post(f"{self.__class__.url}/projects", json={
            "project_key": f"PRJ-WDD",
            "description": f"Project #WDD",
            "is_active": True,
            "labels": ["A", "B", "C"]
        })
        assert response.status_code == 400

        # Check projects is 1
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(3)
    def test_get_project_by_key(self):
        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        # Check no projects
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Add valid test case
        response = requests.post(f"{self.__class__.url}/projects", json={
            "project_key": f"PRJ-SWW",
            "description": f"Project #SDD",
            "is_active": True,
            "labels": ["A", "B", "C", "2", "32", "3"]
        })
        assert response.status_code == 201

        # Get project details
        response = requests.get(f"{self.__class__.url}/projects/PRJ-SWW")
        assert response.status_code == 200
        assert response.json()["project_key"] == f"PRJ-SWW"
        assert response.json()["description"] == f"Project #SDD"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C", "2", "32", "3"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Check projects is 1
        response = requests.get(f"{self.__class__.url}/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(4)
    def test_update_project_by_key(self):
        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")

    @pytest.mark.order(5)
    def test_delete_project_by_key(self):
        logging.info(f"--- Starting test: {self._testMethodName} ---")
        self.__class__.clean_up_db()

        self.__class__.clean_up_db()
        logging.info(f"--- Test: {self._testMethodName} Complete ---")


if __name__ == "__main__":
    unittest.main()
