#!/usr/bin/env python3
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from open_library.time.datetime import now_local


@dataclass
class TimedData:
    data: any
    timestamp: datetime


class TimeDataTracker:
    def __init__(self, time_window_seconds, timeout_seconds):
        self.data = []
        self.time_window = timedelta(seconds=time_window_seconds)
        self.new_data_event = asyncio.Event()
        self.timeout_seconds = timeout_seconds

    async def add_data(self, data_item, timestamp=None):
        if timestamp is None:
            timestamp = now_local()
        timed_data = TimedData(data=data_item, timestamp=timestamp)
        self.data.append(timed_data)
        self.new_data_event.set()
        self.new_data_event.clear()

    async def get_recent_data(self):
        if not self.data or not await self.is_recent_data_valid():
            await self.new_data_event.wait()
        return self.data[-1]

    async def is_recent_data_valid(self):
        if not self.data:
            return False
        recent_data = self.data[-1].timestamp
        current_time = now_local()
        return current_time - recent_data <= self.time_window

    async def wait_for_valid_data(self):
        try:
            return await asyncio.wait_for(
                self.get_recent_data(), timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Timed out waiting for valid data")


# Example usage
async def add_data(data_tracker):
    await data_tracker.add_data("Data1", now_local() - timedelta(seconds=10))
    await asyncio.sleep(1)
    await data_tracker.add_data("Data2", now_local())


async def process_data(data_tracker):
    try:
        recent_data = await data_tracker.wait_for_valid_data()
        print(f"Most recent valid data: {recent_data.data} at {recent_data.timestamp}")
    except TimeoutError as e:
        print(e)


async def main():
    data_tracker = TimedDataTracker(time_window_seconds=60, timeout_seconds=30)
    await asyncio.gather(add_data(data_tracker), process_data(data_tracker))


# asyncio.run(main())
