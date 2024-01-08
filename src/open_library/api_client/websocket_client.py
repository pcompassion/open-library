#!/usr/bin/env python3
import json
import asyncio

from typing import Any, Dict, Optional, Callable, Awaitable
import logging
import websockets

from open_library.logging.logging_filter import WebsocketLoggingFilter


ws_logger = logging.getLogger("websockets.client")
logger = logging.getLogger(__name__)
ws_logger.setLevel(logging.WARNING)


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
        self,
        uri,
        token_manager,
        topic_extractor,
        max_retries=-1,
        initial_delay=1,
        max_delay=30,
    ):
        self.uri = uri
        self.websocket = None
        self.max_retries = max_retries  # -1 indicates infinite retries
        self.retry_count = 0
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.token_manager = token_manager
        self.subscriptions = {}
        self.topic_extractor = topic_extractor  # Function to extract topic from message

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

    async def send(self, header, body):
        header = header or {}
        body = body or {}
        access_token = await self.token_manager.get_access_token()

        header_updated = dict(token=access_token) | header

        payload = {"header": header_updated, "body": body}

        if self.websocket is None or not self.websocket.open:
            await self._connect()

        await self.websocket.send(json.dumps(payload))

    async def subscribe(
        self,
        topic_key,
        handler: Callable,
        header: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
    ):
        # If the topic doesn't exist, create a list for handlers
        if topic_key not in self.subscriptions:
            self.subscriptions[topic_key] = []

        # Add the handler to the list of handlers for this topic
        if handler not in self.subscriptions[topic_key]:
            self.subscriptions[topic_key].append(handler)

        # Start the receive loop if not already running for this topic
        if len(self.subscriptions[topic_key]) == 1:
            # Send a message to subscribe to the topic
            await self.send(header, body)

    async def unsubscribe(
        self,
        topic_key,
        handler: Callable,
        header: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
    ):
        # Remove the handler from the list of handlers for this topic
        if topic_key in self.subscriptions:
            try:
                self.subscriptions[topic_key].remove(handler)
            except ValueError:
                logger.info("Handler not found in the subscription list")

            # If there are no more handlers, cancel the receive task
            if not self.subscriptions[topic_key]:
                await self.send(header, body)

    async def receive(self):
        try:
            while True:
                if self.websocket is None or not self.websocket.open:
                    await self._connect()

                try:
                    message = await self.websocket.recv()
                    logging.info(f"Message received: {message}")

                    response = json.loads(message)
                    topic_key = self.topic_extractor(response)
                    handlers = self.subscriptions.get(topic_key, [])
                    for handler in handlers:
                        await handler(response)
                except (websockets.ConnectionClosed, websockets.ConnectionClosedError):
                    logger.info("Connection closed, calling _connect")
                    await self._connect()
                except Exception as e:
                    logger.exception(f"An error occurred in receive: {e}")

        except asyncio.CancelledError as e:
            logger.info("receive got CancelledError")
        except Exception as e:
            logger.exception(f"An unexpected error occurred in receive: {e}")

    async def close(self):
        topic_keys = list(self.subscriptions.keys())

        for topic_key in topic_keys:
            await self.unsubscribe(topic_key)
        if self.websocket and self.websocket.open:
            await self.websocket.close()
