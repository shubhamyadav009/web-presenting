"""
logger.py

Centralized logging configuration for FinSight - GenAI Financial Analyst Agent.
Provides consistent logging across modules with file + console support.
"""

import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Allow running this module directly (python logger.py) from nested paths.
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from FinSight.utils.constants import LOG_LEVEL, LOG_FORMAT, LOG_DIR


# ----------------------------
# Ensure Log Directory Exists
# ----------------------------

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# ----------------------------
# Logger Factory Function
# ----------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.

    Args:
        name (str): Name of the logger (usually __name__)

    Returns:
        logging.Logger: Configured logger
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # ----------------------------
    # Formatter
    # ----------------------------
    formatter = logging.Formatter(LOG_FORMAT)

    # ----------------------------
    # Console Handler
    # ----------------------------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ----------------------------
    # File Handler (Rotating)
    # ----------------------------
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "finsight.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)

    # ----------------------------
    # Add Handlers
    # ----------------------------
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.propagate = False

    return logger


# ----------------------------
# Default App Logger
# ----------------------------

app_logger = get_logger("FinSight")


# ----------------------------
# Utility Logging Functions
# ----------------------------

def log_info(message: str) -> None:
    app_logger.info(message)


def log_warning(message: str) -> None:
    app_logger.warning(message)


def log_error(message: str) -> None:
    app_logger.error(message)


def log_debug(message: str) -> None:
    app_logger.debug(message)