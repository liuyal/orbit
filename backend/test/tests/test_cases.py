# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging

import pytest

from .test_base import OrbitTMBaseTest


@pytest.mark.order(2)
class TestOrbitTMCases(OrbitTMBaseTest):

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_project(self, session, project_key):
        r = session.post(f"{self.__class__.url}/tm/projects",
                         json={"project_key": project_key})
        assert r.status_code == 201
        return r.json()

    def _create_test_case(self, session, project_key, payload=None):
        r = session.post(
            f"{self.__class__.url}/tm/projects/{project_key}/test-case",
            json=payload or {}
        )
        assert r.status_code == 201
        return r.json()

    # ------------------------------------------------------------------
    # GET /tm/test-cases
    # ------------------------------------------------------------------

    def test_get_all_test_cases(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create multiple projects and test cases
        projects = 5
        cases = 20

        # Create projects and test cases
        for i in range(1, projects + 1):
            # Create project
            project_key = f"PRJ{i}"
            response = session.post(f"{self.__class__.url}/tm/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}"
            })
            assert response.status_code == 201

            # Create test cases for the project
            for j in range(1, cases + 1):
                response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
                    "test_case_key": f"{project_key}-T{j}",
                    "project_key": project_key,
                })
                assert response.status_code == 201

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == projects * cases

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    # ------------------------------------------------------------------
    # GET /tm/projects/{project_key}/test-cases
    # ------------------------------------------------------------------

    def test_get_all_test_cases_by_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create multiple projects and test cases
        projects = 5
        cases = 10

        # Create projects and test cases
        for i in range(1, projects + 1):
            # Create project
            project_key = f"PRJ{i}"
            response = session.post(f"{self.__class__.url}/tm/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}"
            })
            assert response.status_code == 201

            # Create test cases for the project
            for j in range(1, cases + 1):
                response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
                    "test_case_key": f"{project_key}-T{j}",
                    "project_key": project_key
                })
                assert response.status_code == 201

        for i in range(1, projects + 1):
            # Get test cases for each project and verify count
            response = session.get(f"{self.__class__.url}/tm/projects/PRJ{i}/test-cases")
            assert response.status_code == 200
            assert len(response.json()) == cases

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_all_test_cases_by_project_not_found(self, request):
        """GET /projects/{key}/test-cases on a non-existent project → 404."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        response = session.get(f"{self.__class__.url}/tm/projects/PRJ-GHOST/test-cases")
        assert response.status_code == 404
        assert "error" in response.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_all_test_cases_by_project_sorted(self, request):
        """GET /projects/{key}/test-cases returns keys in natural sort order."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-SORT"
        self._create_project(session, project_key)

        # Create 12 test cases with auto-generated keys (T1 … T12)
        for _ in range(12):
            self._create_test_case(session, project_key)

        response = session.get(f"{self.__class__.url}/tm/projects/{project_key}/test-cases")
        assert response.status_code == 200
        keys = [tc["test_case_key"] for tc in response.json()]
        # Natural sort: T1, T2, …, T9, T10, T11, T12  (not T1, T10, T11… lexicographic)
        assert keys == sorted(keys, key=lambda k: int(k.split("T")[-1]))

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    # ------------------------------------------------------------------
    # POST /tm/projects/{project_key}/test-case
    # ------------------------------------------------------------------

    def test_create_test_case_in_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create multiple projects and test cases
        projects = 2
        cases = 15
        count = 0

        # Create projects and test cases
        for i in range(1, projects + 1):
            # Create Test cases for non-existent project (should fail)
            project_key = f"PRJ{i}"
            response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case")
            assert response.status_code == 404

            # Create project
            response = session.post(f"{self.__class__.url}/tm/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}"
            })
            assert response.status_code == 201

            # Create test cases for the project
            for j in range(1, cases + 1):
                count += 1
                response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
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
                assert response.status_code == 201
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
                response = session.get(f"{self.__class__.url}/tm/test-cases")
                assert response.status_code == 200
                assert len(response.json()) == count

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert count == projects * cases
        assert len(response.json()) == projects * cases

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_test_case_default_fields(self, request):
        """Create a test case with no payload — verify auto-key and default field values."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-DEF"
        self._create_project(session, project_key)

        response = session.post(
            f"{self.__class__.url}/tm/projects/{project_key}/test-case",
            json={}
        )
        assert response.status_code == 201
        data = response.json()

        # Auto-generated key must follow the expected pattern
        assert data["test_case_key"] == f"{project_key}-T1"
        assert data["project_key"] == project_key
        assert data["labels"] == []
        assert data["links"] == []
        assert data["test_frequency"] == []
        assert "created_at" in data
        assert "updated_at" in data

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_test_case_auto_key_sequential(self, request):
        """Auto-generated keys must be sequential: T1, T2, T3, …"""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-SEQ"
        self._create_project(session, project_key)

        n = 5
        for expected_n in range(1, n + 1):
            tc = self._create_test_case(session, project_key)
            assert tc["test_case_key"] == f"{project_key}-T{expected_n}"

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_test_case_auto_key_after_manual_skip(self, request):
        """Auto-generated key must not collide with manually-supplied keys that skipped ahead."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-SKIP"
        self._create_project(session, project_key)

        # Manually insert T1, T2, T5 (skipping T3, T4)
        for n in [1, 2, 5]:
            r = session.post(
                f"{self.__class__.url}/tm/projects/{project_key}/test-case",
                json={"test_case_key": f"{project_key}-T{n}"}
            )
            assert r.status_code == 201

        # Next two auto-generated keys must be T6 and T7 (not T3/T4/T5)
        tc6 = self._create_test_case(session, project_key)
        tc7 = self._create_test_case(session, project_key)
        assert tc6["test_case_key"] == f"{project_key}-T6"
        assert tc7["test_case_key"] == f"{project_key}-T7"

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_test_case_invalid_key_format(self, request):
        """Manual key with wrong format must return 400."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-FMT"
        self._create_project(session, project_key)

        for bad_key in [
            "WRONG-T1",           # wrong project prefix
            f"{project_key}-C1",  # wrong type character (C not T)
            f"{project_key}-T",   # missing number
            f"{project_key}-1",   # missing T prefix
        ]:
            r = session.post(
                f"{self.__class__.url}/tm/projects/{project_key}/test-case",
                json={"test_case_key": bad_key}
            )
            assert r.status_code == 400, f"Expected 400 for key '{bad_key}', got {r.status_code}"
            assert "error" in r.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_test_case_duplicate_key(self, request):
        """Creating a test case with an already-used key must return 400."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-DUP"
        self._create_project(session, project_key)
        self._create_test_case(session, project_key, {"test_case_key": f"{project_key}-T1"})

        # Attempt to create the same key again
        r = session.post(
            f"{self.__class__.url}/tm/projects/{project_key}/test-case",
            json={"test_case_key": f"{project_key}-T1"}
        )
        assert r.status_code == 400
        assert "error" in r.json()

        # Count must still be 1
        assert len(session.get(f"{self.__class__.url}/tm/test-cases").json()) == 1

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_create_test_case_labels_propagate_to_project(self, request):
        """Labels added on a test case must be merged into the project's label set."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-LBL"
        self._create_project(session, project_key)

        self._create_test_case(session, project_key, {"labels": ["alpha", "beta"]})
        self._create_test_case(session, project_key, {"labels": ["beta", "gamma"]})

        response = session.get(f"{self.__class__.url}/tm/projects/{project_key}")
        assert response.status_code == 200
        project_labels = set(response.json()["labels"])
        assert {"alpha", "beta", "gamma"}.issubset(project_labels)

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    # ------------------------------------------------------------------
    # DELETE /tm/projects/{project_key}/test-cases
    # ------------------------------------------------------------------

    def test_delete_all_test_cases_by_project(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create multiple projects and test cases
        projects = 3
        cases = 10
        count = 0

        # Create projects and test cases
        for i in range(1, projects + 1):
            # Create project
            project_key = f"PRJ{i}"
            response = session.post(f"{self.__class__.url}/tm/projects", json={
                "project_key": project_key,
                "description": f"Project #{i}"
            })
            assert response.status_code == 201

            # Create test cases for the project
            for j in range(1, cases + 1):
                count += 1
                response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
                    "test_case_key": f"{project_key}-T{j}",
                    "project_key": project_key,
                })
                assert response.status_code == 201

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert count == projects * cases
        assert len(response.json()) == projects * cases

        # Delete test cases for PROJECT 1
        project_key = f"PRJ{1}"
        response = session.delete(f"{self.__class__.url}/tm/projects/{project_key}/test-cases")
        assert response.status_code == 204

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert count == projects * cases
        assert len(response.json()) == projects * cases - cases

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_all_test_cases_by_project_not_found(self, request):
        """DELETE /projects/{key}/test-cases on a non-existent project → 404."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        response = session.delete(f"{self.__class__.url}/tm/projects/PRJ-GHOST/test-cases")
        assert response.status_code == 404
        assert "error" in response.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_all_test_cases_blocked_by_linked_executions(self, request):
        """DELETE all test cases must be blocked when any linked executions exist."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-BLKD"
        self._create_project(session, project_key)
        tc = self._create_test_case(session, project_key)
        tc_key = tc["test_case_key"]

        # Create an execution linked to the test case
        r = session.post(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}/executions",
            json={}
        )
        assert r.status_code == 201

        # Bulk delete must be blocked
        r = session.delete(f"{self.__class__.url}/tm/projects/{project_key}/test-cases")
        assert r.status_code == 400
        assert "error" in r.json()

        # Test case must still exist
        assert len(session.get(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases"
        ).json()) == 1

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    # ------------------------------------------------------------------
    # GET /tm/projects/{project_key}/test-cases/{test_case_key}
    # ------------------------------------------------------------------

    def test_get_test_cases_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create project
        project_key = f"PRJ{1}"
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": project_key,
            "description": f"Project #{1}"
        })
        assert response.status_code == 201

        # Create test cases for the project
        cases = 20
        for j in range(1, cases + 1):
            response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
                "test_case_key": f"{project_key}-T{j}",
                "project_key": project_key,
                "title": f"Test Case {j} for {project_key}",
                "description": f"Description for Test Case {j} in {project_key}",
                "folder": f"/",
                "status": "APPROVED",
                "priority": "NORMAL",
                "test_script": f"x = {j};",
                "test_frequency": ["NIGHTLY"],
                "labels": ["A", "B", "C"],
                "links": [f"http://example.com/test-case/{project_key}-T{j}"]
            })
            assert response.status_code == 201
            assert response.json()["test_case_key"] == f"{project_key}-T{j}"
            assert response.json()["project_key"] == project_key
            assert response.json()["title"] == f"Test Case {j} for {project_key}"
            assert response.json()["description"] == f"Description for Test Case {j} in {project_key}"
            assert response.json()["folder"] == f"/"
            assert response.json()["status"] == "APPROVED"
            assert response.json()["priority"] == "NORMAL"
            assert response.json()["test_script"] == f"x = {j};"
            assert response.json()["test_frequency"] == ["NIGHTLY"]
            assert response.json()["labels"] == ["A", "B", "C"]
            assert response.json()["links"] == [f"http://example.com/test-case/{project_key}-T{j}"]

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == cases

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_get_test_case_by_key_not_found(self, request):
        """GET by key returns 404 for non-existent project or test case key."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-404"
        self._create_project(session, project_key)

        # Non-existent test case key
        r = session.get(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{project_key}-T999")
        assert r.status_code == 404
        assert "error" in r.json()

        # Non-existent project key
        r = session.get(f"{self.__class__.url}/tm/projects/PRJ-GHOST/test-cases/PRJ-GHOST-T1")
        assert r.status_code == 404
        assert "error" in r.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    # ------------------------------------------------------------------
    # PUT /tm/projects/{project_key}/test-cases/{test_case_key}
    # ------------------------------------------------------------------

    def test_update_test_cases_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create project
        project_key = f"PRJ{1}"
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": project_key,
            "description": f"Project #{1}"
        })
        assert response.status_code == 201

        # Create test cases for the project
        j = 1
        response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
            "test_case_key": f"{project_key}-T{j}",
            "project_key": project_key,
            "title": f"Test Case {j} for {project_key}",
            "description": f"Description for Test Case {j} in {project_key}",
            "folder": f"/",
            "status": "APPROVED",
            "priority": "NORMAL",
            "test_script": f"x = {j};",
            "test_frequency": ["NIGHTLY"],
            "labels": ["A", "B", "C"],
            "links": [f"http://example.com/test-case/{project_key}-T{j}"]
        })
        assert response.status_code == 201
        assert response.json()["test_case_key"] == f"{project_key}-T{j}"
        assert response.json()["project_key"] == project_key
        assert response.json()["title"] == f"Test Case {j} for {project_key}"
        assert response.json()["description"] == f"Description for Test Case {j} in {project_key}"
        assert response.json()["folder"] == f"/"
        assert response.json()["status"] == "APPROVED"
        assert response.json()["priority"] == "NORMAL"
        assert response.json()["test_script"] == f"x = {j};"
        assert response.json()["test_frequency"] == ["NIGHTLY"]
        assert response.json()["labels"] == ["A", "B", "C"]
        assert response.json()["links"] == [f"http://example.com/test-case/{project_key}-T{j}"]

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 1

        # Update test case
        response = session.put(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{project_key}-T{j}", json={
            "title": f"Update Test Case {j} for {project_key}",
            "description": f"Update description for Test Case {j} in {project_key}",
            "folder": f"/A",
            "status": "DRAFT",
            "priority": "HIGH",
            "test_script": f"z = {j};",
            "test_frequency": ["NIGHTLY", "WEEKLY"],
            "labels": ["A", "B", "C", "D"],
            "links": [f"http://AAAAA.com/test-case/{project_key}-T{j}"]
        })
        assert response.status_code == 200
        assert response.json()["test_case_key"] == f"{project_key}-T{j}"
        assert response.json()["project_key"] == project_key
        assert response.json()["title"] == f"Update Test Case {j} for {project_key}"
        assert response.json()["description"] == f"Update description for Test Case {j} in {project_key}"
        assert response.json()["folder"] == f"/A"
        assert response.json()["status"] == "DRAFT"
        assert response.json()["priority"] == "HIGH"
        assert response.json()["test_script"] == f"z = {j};"
        assert response.json()["test_frequency"] == ["NIGHTLY", "WEEKLY"]
        assert response.json()["labels"] == ["A", "B", "C", "D"]
        assert response.json()["links"] == [f"http://AAAAA.com/test-case/{project_key}-T{j}"]

        # Get updated test case and verify
        response = session.get(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{project_key}-T{j}")
        assert response.status_code == 200
        assert response.json()["test_case_key"] == f"{project_key}-T{j}"
        assert response.json()["project_key"] == project_key
        assert response.json()["title"] == f"Update Test Case {j} for {project_key}"
        assert response.json()["description"] == f"Update description for Test Case {j} in {project_key}"
        assert response.json()["folder"] == f"/A"
        assert response.json()["status"] == "DRAFT"
        assert response.json()["priority"] == "HIGH"
        assert response.json()["test_script"] == f"z = {j};"
        assert response.json()["test_frequency"] == ["NIGHTLY", "WEEKLY"]
        assert response.json()["labels"] == ["A", "B", "C", "D"]
        assert response.json()["links"] == [f"http://AAAAA.com/test-case/{project_key}-T{j}"]

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_test_case_not_found(self, request):
        """PUT on non-existent project or test case key must return 404."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-UPD"
        self._create_project(session, project_key)

        update_payload = {"title": "irrelevant", "description": "", "folder": "/",
                          "status": "DRAFT", "priority": "NORMAL", "test_script": "",
                          "test_frequency": [], "labels": [], "links": []}

        # Non-existent test case
        r = session.put(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{project_key}-T999",
            json=update_payload
        )
        assert r.status_code == 404
        assert "error" in r.json()

        # Non-existent project
        r = session.put(
            f"{self.__class__.url}/tm/projects/PRJ-GHOST/test-cases/PRJ-GHOST-T1",
            json=update_payload
        )
        assert r.status_code == 404
        assert "error" in r.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_update_test_case_updated_at_changes(self, request):
        """updated_at must advance after PUT; created_at must remain unchanged."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-TS"
        self._create_project(session, project_key)
        tc = self._create_test_case(session, project_key)

        created_at = tc["created_at"]
        updated_at_before = tc["updated_at"]
        tc_key = tc["test_case_key"]

        r = session.put(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}",
            json={"title": "changed", "description": "", "folder": "/",
                  "status": "DRAFT", "priority": "NORMAL", "test_script": "",
                  "test_frequency": [], "labels": [], "links": []}
        )
        assert r.status_code == 200
        updated_at_after = r.json()["updated_at"]

        # Re-fetch and check timestamps
        fetched = session.get(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}"
        ).json()
        assert fetched["created_at"] == created_at
        assert updated_at_after >= updated_at_before

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    # ------------------------------------------------------------------
    # DELETE /tm/projects/{project_key}/test-cases/{test_case_key}
    # ------------------------------------------------------------------

    def test_delete_test_cases_by_key(self, request):
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Create project
        project_key = f"PRJ{1}"
        response = session.post(f"{self.__class__.url}/tm/projects", json={
            "project_key": project_key,
            "description": f"Project #{1}"
        })
        assert response.status_code == 201

        # Create test cases for the project
        cases = 10
        project_key = f"PRJ{1}"
        for j in range(1, cases + 1):
            response = session.post(f"{self.__class__.url}/tm/projects/{project_key}/test-case", json={
                "test_case_key": f"{project_key}-T{j}",
                "project_key": project_key,
            })
            assert response.status_code == 201

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == cases

        # Delete test case by key
        response = session.delete(f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{project_key}-T{1}")
        assert response.status_code == 204

        # Check total test cases
        response = session.get(f"{self.__class__.url}/tm/test-cases")
        assert response.status_code == 200
        assert len(response.json()) == cases - 1

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_test_case_by_key_not_found(self, request):
        """DELETE by key returns 404 for non-existent project or test case."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-DELNF"
        self._create_project(session, project_key)

        # Non-existent test case
        r = session.delete(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{project_key}-T999"
        )
        assert r.status_code == 404
        assert "error" in r.json()

        # Non-existent project
        r = session.delete(
            f"{self.__class__.url}/tm/projects/PRJ-GHOST/test-cases/PRJ-GHOST-T1"
        )
        assert r.status_code == 404
        assert "error" in r.json()

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_test_case_blocked_by_linked_executions(self, request):
        """DELETE a single test case must be blocked when it has linked executions."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-EXLNK"
        self._create_project(session, project_key)
        tc = self._create_test_case(session, project_key)
        tc_key = tc["test_case_key"]

        # Create a linked execution
        r = session.post(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}/executions",
            json={}
        )
        assert r.status_code == 201

        # Delete must be blocked
        r = session.delete(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}"
        )
        assert r.status_code == 400
        assert "error" in r.json()

        # Test case must still exist
        assert session.get(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}"
        ).status_code == 200

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

    def test_delete_test_case_gone_after_deletion(self, request):
        """After deleting a test case, GET must return 404."""
        logging.info(f"--- Starting test: {request.node.name} ---")
        self.__class__.reset_db()

        session = self.__class__.session
        project_key = "PRJ-GONE"
        self._create_project(session, project_key)
        tc = self._create_test_case(session, project_key)
        tc_key = tc["test_case_key"]

        r = session.delete(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}"
        )
        assert r.status_code == 204

        assert session.get(
            f"{self.__class__.url}/tm/projects/{project_key}/test-cases/{tc_key}"
        ).status_code == 404

        self.__class__.reset_db()
        logging.info(f"--- Test: {request.node.name} Complete ---")

