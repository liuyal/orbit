# ================================================================
# Orbit API
# Description: FastAPI backend test script for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import logging
import sys

import pytest


def pytest_addoption(parser):
    """ Add test framework options to the pytest command parser."""

    parser.addoption(
        '--host',
        dest='host',
        default="127.0.0.1",
        help='IP/hostname address of the backend server'
    )
    parser.addoption(
        '--port',
        dest='port',
        default=5000,
        help='Port of the backend server'
    )


def pytest_configure(config):
    """ Called after the command line options have been parsed.
        Configure logging and store options in the pytest namespace.
    """

    option_names = ['host', 'port', 'log_level']
    pytest.options = {opt: config.getoption(opt, None) for opt in option_names}

    log_level_str = "INFO"
    if pytest.options.get("log_level"):
        log_level_str = pytest.options.get("log_level").upper()

    log_level = getattr(logging, log_level_str, logging.INFO)

    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s",
        stream=sys.stdout,
        level=log_level
    )
