# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# app/build_parser.py

import argparse

from backend.app.app_def import TMP_DIR


def build_parser():
    """ Build argument parser. """

    parser = argparse.ArgumentParser(
        description='Orbit FastAPI Backend'
    )
    parser.add_argument(
        '--host',
        dest='host',
        default='0.0.0.0',
        help='Set server host (default:0.0.0.0)'
    )
    parser.add_argument(
        '-p', '--port',
        dest='port',
        default=5000,
        help='Set server listening port (default: 5000)'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output',
        default=TMP_DIR,
        help='Set tmp output directory (default: orbit/backend/tmp)'
    )
    parser.add_argument(
        '-s', '--skip-background-tasks',
        dest='skip_background_tasks',
        action='store_true',
        help='Set skip background task mode'
    )
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='Set debug mode'
    )
    return parser
