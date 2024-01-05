#!/usr/bin/env python3

import time
import asyncio
from functools import wraps, partial
import inspect
from typing import Coroutine, Callable, Any, Awaitable, cast


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


def wrap_func_in_coro(func: Callable[..., Any]):
    """wrap in a coroutine"""

    # If func is already a coroutine or coroutine function, return it as-is
    if asyncio.iscoroutine(func) or asyncio.iscoroutinefunction(func):
        return func

    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            result = await result
        return result

    return wrapper
    # return cast(Coroutine[Any, Any, Any], wrapper)
