# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Version: 0.1.0
# Author: Jerry
# License: MIT
# ================================================================

import argparse
from backend.db.db import DBType

def build_parser():
    """ Build argument parser. """

    parser = argparse.ArgumentParser(
        description='Orbit FastAPI Backend'
    )
    parser.add_argument(
        '--host',
        dest='host',
        default='127.0.0.1',
        help='Set server host (default:127.0.0.1)'
    )
    parser.add_argument(
        '-p', '--port',
        dest='port',
        default=8000,
        help='Set server listening port (default: 8000)'
    )
    parser.add_argument(
        '--db',
        dest='db_type',
        type=lambda x: DBType(x),
        choices=[DBType.MONGODB, DBType.SQLITE],
        default=DBType.MONGODB,
        help='Set database type, choices: mongodb, sqlite. (default: mongodb)'
    )
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='Set server to debug'
    )
    return parser