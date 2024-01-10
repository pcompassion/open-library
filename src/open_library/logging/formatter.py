#!/usr/bin/env python3
import logging
from datetime import datetime
from pathlib import Path


class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%", max_dirs=2, tz=None):
        super().__init__(fmt, datefmt, style)
        self.max_dirs = max_dirs
        # self.converter = (
        #     datetime.now(tz).timetuple if tz else logging.Formatter.converter
        # )

    def format(self, record):
        record.pathname = self.shorten_path(record.pathname)
        return super().format(record)

    def shorten_path(self, path):
        # Use pathlib for cleaner path handling
        path = Path(path)
        parts = path.parts[-self.max_dirs :]
        return str(Path(*parts)) if parts else str(path)
