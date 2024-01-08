#!/usr/bin/env python3
from typing import Any, Callable, ClassVar

from open_library.locator.service_locator import ServiceKey
from open_library.observe.const import ListenerType
from open_library.base_spec.base_spec import BaseSpec


class ListenerSpec(BaseSpec):
    service_key: ServiceKey | None = None

    listener_type: ListenerType
    listener_or_name: Callable | str

    listener_params: dict | None = None
    message_param_name: str | None = None

    service_locator: ClassVar[Any | None] = None

    @classmethod
    def set_service_locator(cls, service_locator):
        cls.service_locator = service_locator

    def get_listener(self) -> Callable | None:
        match self.listener_type:
            case ListenerType.Callable:
                return self.listener_or_name
            case ListenerType.Service:
                service_key = self.service_key

                service = self.service_locator.get_service(service_key)
                listener = getattr(service, self.listener_or_name)

                return listener

        return None
