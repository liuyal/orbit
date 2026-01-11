# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

# tools/tools.py

import pathlib
from datetime import datetime, timezone
from backend.app.app_def import TMP_DIR
import yaml


def configure_logging_file(file_path: pathlib.Path,
                           debug: bool = False) -> str:
    """ Configure logging from file. """

    with open(file_path, 'r') as f:
        conf_text = f.read()

        if debug:
            conf_text = conf_text.replace('<LEVEL>', "DEBUG")

        else:
            conf_text = conf_text.replace('<LEVEL>', "INFO")

        log_conf_text = yaml.safe_load(conf_text)

    log_conf_path = TMP_DIR / 'log_conf.yaml'
    with open(log_conf_path, 'w') as f:
        yaml.dump(log_conf_text, f)

    return str(log_conf_path)


def get_current_utc_time():
    """Get the current UTC time as an ISO formatted string."""

    current_utc_iso = datetime.now(timezone.utc).replace(microsecond=0)
    current_utc_iso = current_utc_iso.isoformat().replace("+00:00", "Z")

    return current_utc_iso
