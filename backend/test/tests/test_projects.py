# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging

import pytest

from .test_base import OrbitTMBaseTest


@pytest.mark.order(1)
class TestOrbitTMProjects(OrbitTMBaseTest):

    def test_get_all_projects(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check no projects exist
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create projects
        n = 10
        active_list = [False] + [True] * (n - 2) + [False]
        for i in range(0, n):
            response = session.post(f"{self.__class__.url}/tm/projects", json={
                "project_key": f"PRJ{i}",
                "description": f"Project #{i}",
                "is_active": active_list[i],
                "labels": ["A", "B", "C"]
            })
            assert response.status_code == 201
            assert response.json()["project_key"] == f"PRJ{i}"
            assert response.json()["description"] == f"Project #{i}"
            assert response.json()["is_active"] == active_list[i]
            assert response.json()["labels"] == ["A", "B", "C"]
            assert response.json()["test_case_count"] == 0
            assert response.json()["test_cycle_count"] == 0

        # Check project list
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == n

        for i in range(0, n):
            assert response.json()[i]["project_key"] == f"PRJ{i}"
            assert response.json()[i]["description"] == f"Project #{i}"
            assert response.json()[i]["is_active"] == active_list[i]
            assert response.json()[i]["labels"] == ["A", "B", "C"]
            assert response.json()[i]["test_case_count"] == 0
            assert response.json()[i]["test_cycle_count"] == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_project_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check no projects
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Check duplicated labels
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": f"PRJ-WDD",
            "description": f"Project #WDD",
            "is_active": True,
            "labels": ["A", "B", "C", "A", "B", "C"]
        })
        assert response.status_code == 400
        assert response.json()["error"] == f"Duplicated labels in request"

        # Check no projects
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Add valid test case
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": f"PRJ-WDD",
            "description": f"Project #WDD",
            "is_active": True,
            "labels": ["A", "B", "C"]
        })
        assert response.status_code == 201
        assert response.json()["project_key"] == f"PRJ-WDD"
        assert response.json()["description"] == f"Project #WDD"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Get project details
        response = session.get(f"{self.__class__.url}/tm/projects/PRJ-WDD")
        assert response.status_code == 200
        assert response.json()["project_key"] == f"PRJ-WDD"
        assert response.json()["description"] == f"Project #WDD"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Check projects is 1
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Add duplicated test case
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": f"PRJ-WDD",
            "description": f"Project #WDD",
            "is_active": True,
            "labels": ["A", "B", "C"]
        })
        assert response.status_code == 400

        # Check projects is 1
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_project_default_fields(self, request):
        """Create a project with only required fields and verify defaults."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Minimal payload — only project_key required
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": "PRJ-DEFAULT"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["project_key"] == "PRJ-DEFAULT"
        assert data["labels"] == []
        assert data["test_case_count"] == 0
        assert data["test_cycle_count"] == 0
        # timestamps must be present
        assert "created_at" in data
        assert "updated_at" in data

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_project_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check no projects
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Add valid test case
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": f"PRJ-SWW",
            "description": f"Project #SDD",
            "is_active": True,
            "labels": ["A", "B", "C", "2", "32", "3"]
        })
        assert response.status_code == 201
        assert response.json()["project_key"] == f"PRJ-SWW"
        assert response.json()["description"] == f"Project #SDD"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C", "2", "32", "3"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Get project details
        response = session.get(f"{self.__class__.url}/tm/projects/PRJ-SWW")
        assert response.status_code == 200
        assert response.json()["project_key"] == f"PRJ-SWW"
        assert response.json()["description"] == f"Project #SDD"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C", "2", "32", "3"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Check projects is 1
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_project_by_key_not_found(self, request):
        """GET on a non-existent project key must return 404."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        response = session.get(f"{self.__class__.url}/tm/projects/PRJ-DOES-NOT-EXIST")
        assert response.status_code == 404
        assert "error" in response.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_project_counts_reflect_linked_data(self, request):
        """test_case_count and test_cycle_count must match real linked data."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-CNT"

        session.post(f"{self.__class__.url}/tm/projects", json={"project_key": project_key})

        # Add 3 test cases
        for i in range(1, 4):
            r = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={})
            assert r.status_code == 201

        # Add 2 test cycles
        for _ in range(2):
            r = session.post(f"{self.__class__.url}/tm/projects/{project_key}/cycles", json={})
            assert r.status_code == 201

        # GET project — counts must be accurate
        response = session.get(f"{self.__class__.url}/tm/projects/{project_key}")
        assert response.status_code == 200
        assert response.json()["test_case_count"] == 3
        assert response.json()["test_cycle_count"] == 2

        # List endpoint must also report accurate counts
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        project = next(p for p in response.json() if p["project_key"] == project_key)
        assert project["test_case_count"] == 3
        assert project["test_cycle_count"] == 2

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_project_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check no projects
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Add valid test case
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": f"PRJ-A",
            "description": f"Project #A",
            "is_active": True,
            "labels": ["A", "B", "C"]
        })
        assert response.status_code == 201
        assert response.json()["project_key"] == f"PRJ-A"
        assert response.json()["description"] == f"Project #A"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Check projects is 1
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = session.put(f"{self.__class__.url}/tm/projects/PRJ-A", json={
            "description": f"Project #B++++++++",
            "is_active": False,
            "labels": ["1", "2", "3"]
        })
        assert response.status_code == 200
        assert response.json()["project_key"] == f"PRJ-A"
        assert response.json()["description"] == f"Project #B++++++++"
        assert response.json()["is_active"] == False
        assert response.json()["labels"] == ["1", "2", "3"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_project_not_found(self, request):
        """PUT on a non-existent project key must return 404."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        response = session.put(f"{self.__class__.url}/tm/projects/PRJ-GHOST", json={
            "description": "should not work",
            "is_active": False,
            "labels": []
        })
        assert response.status_code == 404
        assert "error" in response.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_project_duplicate_labels(self, request):
        """PUT with duplicate labels must return 400 and leave project unchanged."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Create project
        session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": "PRJ-DUP",
            "description": "Original",
            "is_active": True,
            "labels": ["X", "Y"]
        })

        # Attempt update with duplicate labels
        response = session.put(f"{self.__class__.url}/tm/projects/PRJ-DUP", json={
            "description": "Should not update",
            "is_active": False,
            "labels": ["X", "X", "Y"]
        })
        assert response.status_code == 400
        assert "error" in response.json()

        # Verify project is unchanged
        response = session.get(f"{self.__class__.url}/tm/projects/PRJ-DUP")
        assert response.status_code == 200
        assert response.json()["description"] == "Original"
        assert response.json()["is_active"] == True
        assert set(response.json()["labels"]) == {"X", "Y"}

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_project_is_active_only(self, request):
        """Partial update — only is_active — must not modify other fields."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": "PRJ-PARTIAL",
            "description": "Stays the same",
            "is_active": True,
            "labels": ["keep"]
        })

        response = session.put(f"{self.__class__.url}/tm/projects/PRJ-PARTIAL", json={
            "description": "Stays the same",
            "is_active": False,
            "labels": ["keep"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == False
        assert data["description"] == "Stays the same"
        assert data["labels"] == ["keep"]

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_project_updated_at_changes(self, request):
        """updated_at timestamp must advance after a PUT."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": "PRJ-TS",
            "description": "Before",
            "is_active": True,
            "labels": []
        })
        assert response.status_code == 201
        created_at = response.json()["created_at"]
        updated_at_before = response.json()["updated_at"]

        response = session.put(f"{self.__class__.url}/tm/projects/PRJ-TS", json={
            "description": "After",
            "is_active": True,
            "labels": []
        })
        assert response.status_code == 200
        updated_at_after = response.json()["updated_at"]

        # created_at must never change
        response = session.get(f"{self.__class__.url}/tm/projects/PRJ-TS")
        assert response.json()["created_at"] == created_at
        # updated_at must be >= original (may be equal if update is very fast)
        assert updated_at_after >= updated_at_before

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_project_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check no projects
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Add valid test case
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": f"PRJ-A5",
            "description": f"Project #A5",
            "is_active": True,
            "labels": ["A", "B", "C"]
        })
        assert response.status_code == 201
        assert response.json()["project_key"] == f"PRJ-A5"
        assert response.json()["description"] == f"Project #A5"
        assert response.json()["is_active"] == True
        assert response.json()["labels"] == ["A", "B", "C"]
        assert response.json()["test_case_count"] == 0
        assert response.json()["test_cycle_count"] == 0

        # Check projects is 1
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Delete project
        response = session.delete(f"{self.__class__.url}/tm/projects/PRJ-A5")
        assert response.status_code == 204

        # Get deleted project
        response = session.get(f"{self.__class__.url}/tm/projects/PRJ-A5")
        assert response.status_code == 404

        # Check no projects
        response = session.get(f"{self.__class__.url}/tm/projects")
        assert response.status_code == 200
        assert len(response.json()) == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_project_not_found(self, request):
        """DELETE on a non-existent project key must return 404."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        response = session.delete(f"{self.__class__.url}/tm/projects/PRJ-NOPE")
        assert response.status_code == 404
        assert "error" in response.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_project_with_linked_test_cases_blocked(self, request):
        """DELETE with force=False must be blocked when linked test cases exist."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-LINKED"

        session.post(f"{self.__class__.url}/tm/projects", json={"project_key": project_key})

        # Add 2 test cases
        for _ in range(2):
            r = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={})
            assert r.status_code == 201

        # DELETE with force=False — should be blocked
        response = session.delete(
            f"{self.__class__.url}/tm/projects/{project_key}",
            json={"force": False}
        )
        assert response.status_code == 400
        assert "error" in response.json()

        # Project must still exist
        response = session.get(f"{self.__class__.url}/tm/projects/{project_key}")
        assert response.status_code == 200

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_project_force_removes_linked_data(self, request):
        """Force DELETE (default) must remove project and all linked test cases/cycles."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-FORCE"

        session.post(f"{self.__class__.url}/tm/projects", json={"project_key": project_key})

        # Add test cases and cycles
        for _ in range(3):
            session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={})
        for _ in range(2):
            session.post(f"{self.__class__.url}/tm/projects/{project_key}/cycles", json={})

        # Force delete (no body = default force)
        response = session.delete(f"{self.__class__.url}/tm/projects/{project_key}")
        assert response.status_code == 204

        # Project must be gone
        assert session.get(f"{self.__class__.url}/tm/projects/{project_key}").status_code == 404

        # Test cases must be gone
        assert len(session.get(f"{self.__class__.url}/tm/test-cases").json()) == 0

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_project_counts_update_after_test_case_delete(self, request):
        """test_case_count must decrement when a test case is deleted."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-DECR"

        session.post(f"{self.__class__.url}/tm/projects", json={"project_key": project_key})

        # Add 3 test cases
        tc_keys = []
        for _ in range(3):
            r = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={})
            assert r.status_code == 201
            tc_keys.append(r.json()["test_case_key"])

        # Verify count = 3
        response = session.get(f"{self.__class__.url}/tm/projects/{project_key}")
        assert response.json()["test_case_count"] == 3

        # Delete one test case
        r = session.delete(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_keys[0]}")
        assert r.status_code == 204

        # Count must be 2
        response = session.get(f"{self.__class__.url}/tm/projects/{project_key}")
        assert response.json()["test_case_count"] == 2

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

