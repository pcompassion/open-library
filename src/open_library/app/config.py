#!/usr/bin/env python3
from open_library.locator.service_locator import ServiceKey


class BaseConfig:
    service_key = ServiceKey(
        service_type="config",
        service_name="base_config",
    )

    def __init__(self):
        self._initialized = False
        self.environment = None

    def initialize(self, environment):
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
            return self.__dict__[name]
        except KeyError:
            raise AttributeError("Config has no attribute '{}'".format(name))
