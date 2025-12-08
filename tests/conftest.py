# ================================================================
# Orbit API
# Description: FastAPI backend sanity test script for the Orbit application.
# Version: 0.1.0
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
        default=8000,
        help='Port of the backend server'
    )
    parser.addoption(
        '--protocol',
        dest='protocol',
        default="http",
        help='Protocol to connect to the backend server'
    )
    parser.addoption(
        '--debug-log',
        dest='debug-log',
        action='store_true',
        help='Set debug verbose output'
    )


def pytest_configure(config):
    """ Called after the command line options have been parsed.
        Configures the logger and sets the command line options for use with bdd_main.py
    """

    option_names = ['host',
                    'port',
                    'protocol',
                    'debug-log']

    pytest.options = {opt: config.getoption(opt, None) for opt in option_names}
    debug = pytest.options["debug-log"]

    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s",
        stream=sys.stdout,
        level=logging.INFO if not debug else logging.DEBUG)
