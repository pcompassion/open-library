#!/usr/bin/env python3
from open_library.environment.const import Env
from dotenv import load_dotenv
from pathlib import Path
import os
import pytz
from typing import Any
import json
import pendulum


class Environment:
    def __init__(self, env_directory: str = "", env_file: str = ".env") -> None:
        self.env_file = env_file
        self.directory = env_directory
        self.cur_directory = Path(os.getcwd())

        base_dir = Path(self.directory or self.cur_directory).resolve()

        dotenv_path = base_dir / env_file
        load_dotenv(dotenv_path)

        self.env = Env(os.getenv("ENV"))
        self.local_timezone = pytz.timezone("Asia/Seoul")
        pendulum.set_local_timezone(self.local_timezone)

    def is_dev(self) -> bool:
        return self.env == Env.DEV

    def is_prod(self) -> bool:
        return self.env == Env.PROD

    def get(self, key: str, default_value: Any = "") -> Any:
        return os.getenv(key, default_value)

    def get_json(self, key: str, default_value: Any = "") -> Any:
        return json.loads(os.getenv(key, default_value))
