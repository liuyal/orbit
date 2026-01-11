# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Version: 0.1.0
# Author: Jerry
# License: MIT
# ================================================================

# tools/build_parser.py

import argparse
import pathlib


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
        default=pathlib.Path(__file__).parents[1] / 'tmp',
        help='Set output directory (default: /tmp)'
    )
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='Set server to debug'
    )
    return parser
