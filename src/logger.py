"""
Shared logging setup for the agentic workflow.

A single logger is used by planner/actor/checker/agent so the whole
plan -> act -> check decision trail ends up interleaved, in order, in one
place (console + a timestamped file under logs/). Without this, debugging
"why did attempt 2 behave differently" would mean stitching together
print statements from four different modules by hand.
"""

import logging
import os
from datetime import datetime, timezone

LOG_DIR = "logs"
_LOGGER_NAME = "agent"
_configured = False


def get_logger() -> logging.Logger:
    """
    Returns the shared agent logger, configuring it on first use.

    Idempotent by design: agent.py, planner.py, actor.py, and checker.py
    each call this independently. Without the _configured guard, importing
    the modules in certain orders would attach duplicate handlers and every
    log line would print twice.
    """
    global _configured

    logger = logging.getLogger(_LOGGER_NAME)

    if _configured:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(module)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        log_path = os.path.join(LOG_DIR, f"run_{timestamp}.log")

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info("Logging to %s", log_path)
    except OSError as exc:
        # A read-only filesystem or permissions issue shouldn't stop the
        # agent from running -- console logging alone is degraded but fine.
        logger.warning("Could not create log file (%s); continuing with console logging only", exc)

    _configured = True
    return logger
