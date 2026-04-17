# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import pathlib
# app/utility.py
from collections import Counter
from datetime import datetime, timezone

import yaml

from backend.app.app_def import TMP_DIR


def configure_logging(file_path: pathlib.Path,
                      debug: bool = False) -> str:
    """ Configure logging from file. """

    with open(file_path, 'r') as f:
        conf_text = f.read()

        if debug:
            conf_text = conf_text.replace('<LEVEL>', "DEBUG")

        else:
            conf_text = conf_text.replace('<LEVEL>', "INFO")

        log_conf_text = yaml.safe_load(conf_text)

    with open(TMP_DIR / file_path.name, 'w') as f:
        yaml.dump(log_conf_text, f)

    return str(TMP_DIR / file_path.name)


def get_current_utc_time():
    """Get the current UTC time as an ISO formatted string."""

    current_utc_iso = datetime.now(timezone.utc).replace(microsecond=0)
    current_utc_iso = current_utc_iso.isoformat().replace("+00:00", "Z")

    return current_utc_iso


def calculate_cycle_status(cycle_data: dict):
    """Calculate cycle status from cycle data."""

    # Count cycle status
    counts = Counter(cycle_data["executions"].values())

    # assign status of cycle base on execution status
    if counts.get("NOT_EXECUTED", 0) > 0:
        if counts.get("NOT_EXECUTED", 0) == len(cycle_data["executions"]):
            cycle_data["status"] = "NOT_STARTED"

        else:
            cycle_data["status"] = "IN_PROGRESS"

    else:
        if len(cycle_data["executions"]) == 0:
            cycle_data["status"] = "NOT_STARTED"

        else:
            cycle_data["status"] = "COMPLETE"

    return cycle_data
