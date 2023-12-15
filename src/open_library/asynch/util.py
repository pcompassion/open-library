#!/usr/bin/env python3

import time
import asyncio


async def periodic_wrapper(interval: float, coro_func, *args, **kwargs):
    """Run coro_func with args every interval seconds."""
    while True:
        start_time = time.monotonic()
        should_terminate = await coro_func(
            *args, **kwargs
        )  # Run the coroutine function with arguments
        if should_terminate:
            return
        elapsed = time.monotonic() - start_time
        await asyncio.sleep(max(interval - elapsed, 0))
