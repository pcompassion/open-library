#!/usr/bin/env python3

from functools import singledispatchmethod
from typing import Callable

from open_library.observe.listener_spec import ListenerSpec
from open_investing.event_spec.event_spec import EventSpec
import asyncio
from open_library.observe.const import ListenerType
from open_library.observe.listener_spec import ListenerSpec

from open_library.observe.subscription_manager import SubscriptionManager


class PubsubBroker:
    def __init__(self):
        self.subscription_manager = SubscriptionManager()

        self.queue = asyncio.Queue()
        self.running = False

    @singledispatchmethod
    def subscribe(self, event_spec, listener_spec):
        raise NotImplementedError

    @subscribe.register
    async def _(self, task_spec: EventSpec, listener_spec: Callable):
        listener_spec_ = ListenerSpec(
            listener_type=ListenerType.Callable,
            listener_or_name=listener_spec,
        )
        return await self.subscribe(task_spec, listener_spec_)

    @subscribe.register
    async def _(self, task_spec: EventSpec, listener_spec: ListenerSpec):
        self.subscription_manager.subscribe(task_spec, listener_spec)

    @singledispatchmethod
    def unsubscribe(self, task_spec, listener_spec):
        raise NotImplementedError

    @unsubscribe.register
    async def _(self, task_spec: EventSpec, listener_spec: Callable):
        listener_spec_ = ListenerSpec(
            listener_type=ListenerType.Callable,
            listener_or_name=listener,
        )
        return await self.unsubscribe(task_spec, listener_spec_)

    @unsubscribe.register
    async def _(self, task_spec: EventSpec, listener_spec: ListenerSpec):
        self.subscription_manager.unsubscribe(task_spec, listener_spec)

    async def run(self):
        self.running = True
        while self.running:
            message = await self.queue.get()
            await self.subscription_manager.publish(message)

    def stop_processing(self):
        self.running = False

    async def enqueue_message(self, message: dict):
        await self.queue.put(message)
