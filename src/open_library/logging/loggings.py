#!/usr/bin/env python3

import logging
import logging.config
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from open_library.logging.logging_filter import IntervalLoggingFilter

LOG_FILE_NAME = "app.log"
LOG_ERROR_FILE_NAME = "app-error.log"

F_LOG_FILE_NAME = "{app_name}.log"
F_LOG_ERROR_FILE_NAME = "{app_name}-error.log"


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname:8s} {asctime} [{filename}:{lineno:04d}] {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d:%H:%M:%S",
        },
        "mid": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "verbose",
        },
        "simple-file": {
            "class": "logging.FileHandler",
            "filename": "app-simple.log",
            "level": "DEBUG",
            "formatter": "verbose",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE_NAME,
            "when": "midnight",  #
            "formatter": "verbose",
            "backupCount": 7,
        },
        "error-file": {
            "level": "WARNING",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_ERROR_FILE_NAME,
            "when": "midnight",  #
            "formatter": "verbose",
            "backupCount": 7,
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "focus-logger": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
        "interval-logger": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
    },
}


def setup_logging(log_dir_path, log_to_file=True, app_name="app", tz=None):
    log_dir_path = log_dir_path or Path(".")

    class TimeFormatter(logging.Formatter):
        converter = lambda *args: datetime.now(tz).timetuple()

    if tz:
        LOGGING_CONFIG["formatters"]["verbose"]["()"] = TimeFormatter

    print("logging directory", str(log_dir_path))
    log_dir_path.mkdir(parents=True, exist_ok=True)

    log_file_name = F_LOG_FILE_NAME.format(app_name=app_name)
    log_error_file_name = F_LOG_ERROR_FILE_NAME.format(app_name=app_name)

    # Set the filepath for the log file
    filepath = str(log_dir_path / log_file_name)
    error_filepath = str(log_dir_path / log_error_file_name)

    LOGGING_CONFIG["handlers"]["file"]["filename"] = filepath
    LOGGING_CONFIG["handlers"]["error-file"]["filename"] = error_filepath

    if log_to_file:
        default_handlers = LOGGING_CONFIG["loggers"][""]["handlers"]
        if "file" not in default_handlers:
            default_handlers.append("file")

    logging.config.dictConfig(LOGGING_CONFIG)

    # interval logger
    interval_filter = IntervalLoggingFilter(interval=60)
    interval_logger = logging.getLogger("interval-logger")
    interval_logger.addFilter(interval_filter)
