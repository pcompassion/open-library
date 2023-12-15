#!/usr/bin/env python3
import json
import asyncio

from typing import Any, Dict, Optional, Callable, Awaitable
import logging
import websockets

from risk_glass.ebest.openapi.log_utils import WebsocketLoggingFilter


ws_logger = logging.getLogger("websockets.client")
logger = logging.getLogger(__name__)


class CustomWebSocketClient(websockets.WebSocketClientProtocol):
    async def ping(self, data: Optional[Any] = None) -> Awaitable[None]:
        # for debug
        # logger.info("keepalive_ping")

        return await super().ping(data)


class NoPingPongFilter(logging.Filter):
    def filter(self, record):
        # Filter out ping/pong log messages
        return not ("ping" in record.getMessage() or "pong" in record.getMessage())


ws_filter = WebsocketLoggingFilter(60)  # Log once every 60 seconds
ws_logger.addFilter(ws_filter)


class WebSocketClient:
    def __init__(
        self, uri, headers, token_manager, max_retries=-1, initial_delay=1, max_delay=30
    ):
        self.uri = uri
        self.websocket = None
        self.max_retries = max_retries  # -1 indicates infinite retries
        self.retry_count = 0
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.token_manager = token_manager
        self.headers = headers
        self.subscriptions = {}

    async def _connect(self):
        while self.retry_count != self.max_retries:
            try:
                self.websocket = await websockets.connect(
                    self.uri, create_protocol=CustomWebSocketClient
                )
                self.retry_count = 0  # reset retry count on successful connect
                return
            except ConnectionRefusedError:
                self.retry_count += 1
                backoff = min(
                    self.initial_delay * (2**self.retry_count), self.max_delay
                )
                await asyncio.sleep(backoff)

        raise ConnectionRefusedError("Maximum retry count reached")

    async def receive(self, handler):
        try:
            while True:
                if self.websocket is None or not self.websocket.open:
                    await self._connect()

                try:
                    message = await self.websocket.recv()
                    await handler(message)
                except (websockets.ConnectionClosed, websockets.ConnectionClosedError):
                    logger.info("receive calling _connect")

                    await self._connect()

        except asyncio.CancelledError:
            logger.info("receive got CancelledError")

            return

    async def send(self, body):
        access_token = await self.token_manager.get_access_token()
        self.headers["token"] = access_token

        payload = {"header": self.headers, "body": body}

        if self.websocket is None or not self.websocket.open:
            await self._connect()

        await self.websocket.send(json.dumps(payload))

    async def subscribe(self, body: Dict[str, str], topic_key: tuple, handler=None):
        # Send a message to subscribe to the topic.

        await self.send(body)

        # If not already receiving, start the loop.
        if topic_key not in self.subscriptions:
            self.subscriptions[topic_key] = asyncio.create_task(self.receive(handler))

    async def unsubscribe(self, topic_key):
        task = self.subscriptions.pop(topic_key, None)
        if task:
            logger.info("cancelling task")
            task.cancel()
            try:
                # Wait for the task to be cancelled.
                await task
            finally:
                pass

    async def close(self):
        topic_keys = list(self.subscriptions.keys())

        for topic_key in topic_keys:
            await self.unsubscribe(topic_key)
        if self.websocket and self.websocket.open:
            await self.websocket.close()
