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
