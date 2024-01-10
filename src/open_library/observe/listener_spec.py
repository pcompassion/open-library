#!/usr/bin/env python3
from typing import Any, Callable, ClassVar, Coroutine

from open_library.locator.service_locator import ServiceKey
from open_library.observe.const import ListenerType
from open_library.base_spec.base_spec import BaseSpec
from channels.layers import get_channel_layer
from open_library.asynch.util import wrap_func_in_coro


class ListenerSpec(BaseSpec):
    service_key: ServiceKey | None = None

    listener_type: ListenerType
    listener_or_name: Callable | str

    service_locator: ClassVar[Any | None] = None

    @classmethod
    def set_service_locator(cls, service_locator):
        cls.service_locator = service_locator

    def get_listener_coroutine(self, message) -> Coroutine[Any, Any, None]:
        match self.listener_type:
            case ListenerType.Callable:
                listener = self.listener_or_name
                coroutine = wrap_func_in_coro(listener)
                return coroutine(message)
            case ListenerType.Service:
                service_key = self.service_key

                service = self.service_locator.get_service(service_key)
                listener = getattr(service, self.listener_or_name)
                coroutine = wrap_func_in_coro(listener)
                return coroutine(message)

            case ListenerType.ChannelGroup:
                channel_layer = get_channel_layer()
                group_name = self.listener_or_name
                return channel_layer.group_send(
                    group_name, {"type": "task_message", "message": message}
                )

        return None
