#!/usr/bin/env python3
import pendulum


class BaseApp:
    name = "base_app"

    def __init__(self):
        self.environment = None

    def setup_logging(self):
        from open_library.logging.loggings import setup_logging

        log_to_file = self.environment.get("LOG_TO_FILE", False)
        log_dir_path = self.environment.cur_directory / "logs"

        local_timezone = self.environment.local_timezone

        setup_logging(
            log_dir_path, log_to_file=log_to_file, app_name=self.name, tz=local_timezone
        )
