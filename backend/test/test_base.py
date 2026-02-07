# ================================================================
# Orbit API
# Description: FastAPI backend sanity test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging
import unittest

import pytest
import requests


class OrbitTMBaseTest(unittest.TestCase):
    """Base class for Orbit backend tests."""

    @classmethod
    def setUpClass(cls):
        """Initialize test class"""

        logging.info(f"Initialize tests...")

        cls.host = pytest.options['host']
        cls.port = pytest.options['port']

        cls.protocol = "http"
        cls.url = f"{cls.protocol}://{cls.host}:{cls.port}/api/v1/tm"

        response = requests.get(f"{cls.protocol}://{cls.host}:{cls.port}/")
        assert response.status_code == 204

    @classmethod
    def tearDownClass(cls):
        """Teardown test class"""

        logging.info(f"Teardown tests...")
        cls.clean_up_db()

    @classmethod
    def clean_up_db(cls):
        """Clean up the database"""

        response = requests.post(f"{cls.url}/reset")
        assert response.status_code == 204
