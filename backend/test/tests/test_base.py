# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging

import pytest
import requests


class OrbitTMBaseTest:
    """Base class for Orbit backend tests."""

    @classmethod
    def setup_class(cls):
        """Initialize test class"""

        logging.debug(f"Initialize tests...")

        cls.host = pytest.options['host']
        cls.port = pytest.options['port']

        cls.protocol = "http"
        cls.url = f"{cls.protocol}://{cls.host}:{cls.port}/api/v1/tm"

        response = requests.get(f"{cls.protocol}://{cls.host}:{cls.port}/")
        assert response.status_code == 204

    @classmethod
    def teardown_class(cls):
        """Teardown test class"""

        logging.debug(f"Teardown tests...")

    @classmethod
    def reset_db(cls):
        """Reset the database"""

        response = requests.post(f"{cls.url}/reset")
        assert response.status_code == 204
