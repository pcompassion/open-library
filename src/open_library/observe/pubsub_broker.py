#!/usr/bin/env python3


from open_library.observe.listener_spec import ListenerSpec
from open_investing.event_spec.event_spec import EventSpec
import asyncio

from open_library.observe.subscription_manager import SubscriptionManager


class PubsubBroker:
    def __init__(self):
        self.subscription_manager = SubscriptionManager()

        self.queue = asyncio.Queue()
        self.running = False

    def subscribe(self, event_spec: EventSpec, listener_spec: ListenerSpec):
        self.subscription_manager.subscribe(event_spec, listener_spec)

    def unsubscribe(self, event_spec: EventSpec, listener_spec: ListenerSpec):
        self.subscription_manager.unsubscribe(event_spec, listener_spec)

    async def start_processing(self):
        self.running = True
        while self.running:
            event_spec = await self.queue.get()
            await self.subscription_manager.publish(message)

    def stop_processing(self):
        self.running = False

    async def enqueue_message(self, message: dict):
        await self.queue.put(message)
