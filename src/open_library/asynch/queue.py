#!/usr/bin/env python3


import asyncio


class DroppingQueue(asyncio.Queue):
    def __init__(self, maxsize, *args, **kwargs):
        super().__init__(maxsize, *args, **kwargs)

    async def put(self, item):
        # If the queue is full, remove the oldest item
        while self.full():
            self.get_nowait()
        # Put the new item into the queue
        await super().put(item)


async def call_function_after_delay(func, delay_seconds=3, *args, **kwargs):
    await asyncio.sleep(delay_seconds)
    await func(*args, **kwargs)
