#!/usr/bin/env python3
import pendulum
from open_library.environment.environment import Environment


class BaseApp:
    name = "base_app"

    def __init__(self, env_directory, env_file):
        self.environment = Environment(env_directory=env_directory, env_file=env_file)

        self.setup_logging()

    def setup_logging(self):
        from open_library.logging.loggings import setup_logging

        log_to_file = self.environment.get("LOG_TO_FILE", False)
        log_dir_path = self.environment.cur_directory / "logs"

        local_timezone = self.environment.local_timezone

        setup_logging(
            log_dir_path, log_to_file=log_to_file, app_name=self.name, tz=local_timezone
        )
