#!/usr/bin/env python3


import asyncio


class PubsubBroker:
    def __init__(self):
        self.subscribers: dict[str, set] = {}
        self.queue = asyncio.Queue()
        self.running = False

    def subscribe(self, key: str, listener):
        if key not in self.subscribers:
            self.subscribers[key] = set()
        self.subscribers[key].add(listener)

    def unsubscribe(self, key: str, listener):
        if key in self.subscribers:
            self.subscribers[key].remove(listener)

    async def start_processing(self):
        self.running = True
        while self.running:
            key, message = await self.queue.get()
            await self.publish(key, message)

    def stop_processing(self):
        self.running = False

    async def enqueue_message(self, key: str, message):
        await self.queue.put((key, message))

    async def publish(self, key: str, message):
        if key in self.subscribers:
            for listener in self.subscribers[key]:
                asyncio.create_task(listener(message))
