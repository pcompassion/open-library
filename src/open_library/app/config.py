#!/usr/bin/env python3
from open_library.locator.service_locator import ServiceKey
from open_library.environment.environment import Environment


class BaseConfig:
    service_key = ServiceKey(
        service_type="config",
        service_name="base_config",
    )

    def __init__(self):
        self._initialized = False
        self.environment = None

    def initialize(self, environment: Environment):
        self.environment = environment
        self._initialized = True

    @property
    def initialized(self):
        return self._initialized

    def __getattr__(self, name):
        if not self._initialized:
            raise Exception(
                "Attempted to access config attribute '{}' before initialization".format(
                    name
                )
            )

        try:
            if self.environment:
                value = self.environment.get(name, None)
                if value:
                    return value

            return self.__dict__[name]
        except KeyError:
            raise AttributeError("Config has no attribute '{}'".format(name))

    def __getattr__(self, name):
        if not self._initialized:
            raise Exception(
                "Attempted to access config attribute '{}' before initialization".format(
                    name
                )
            )

        try:
            if self.environment:
                value = self.environment.get(name, None)
                if value:
                    return value

            return self.__dict__[name]
        except KeyError:
            raise AttributeError("Config has no attribute '{}'".format(name))

    def is_enabled(self, name: str) -> bool:
        try:
            value = self.__getattr__(name)
            if isinstance(value, str):
                return value.strip().lower() in ["true", "yes", "1"]

            return bool(value)
        except AttributeError:
            # If __getattr__ raises AttributeError, the attribute is not set
            return False
