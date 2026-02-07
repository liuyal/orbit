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
        default=5000,
        help='Port of the backend server'
    )
    parser.addoption(
        '--protocol',
        dest='protocol',
        default="http",
        help='Protocol to connect to the backend server'
    )
    parser.addoption(
        '--loglevel',
        dest='loglevel',
        default='INFO',
        help='Set logging level'
    )


def pytest_configure(config):
    """ Called after the command line options have been parsed.
        Configures the logger and sets the command line options for use with bdd_main.py
    """

    option_names = ['host',
                    'port',
                    'protocol',
                    'loglevel']

    pytest.options = {opt: config.getoption(opt, None) for opt in option_names}
    loglevel_str = pytest.options["loglevel"].upper()
    loglevel = getattr(logging, loglevel_str, logging.INFO)

    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(levelname)s: %(message)s",
        stream=sys.stdout,
        level=loglevel)
