#!/usr/bin/env python3
from dataclasses import dataclass
import json
import asyncio

from typing import Any, Dict, Optional, Callable, Awaitable
import logging
import websockets

from open_library.logging.logging_filter import WebsocketLoggingFilter


ws_logger = logging.getLogger("websockets.client")
logger = logging.getLogger(__name__)
# ws_logger.setLevel(logging.WARNING)


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


@dataclass
class SubscriptionData:
    handler: callable
    header: dict[str, str]
    body: dict[str, str]


class WebSocketClient:
    def __init__(
        self,
        uri,
        token_manager,
        topic_extractor,
        max_retries=10,
        initial_delay=1,
        max_delay=300,
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
        self.receive_task = None

    async def _connect(self):
        backoff = self.initial_delay
        while self.retry_count != self.max_retries:
            logger.info(
                f"_connect, retry_count: {self.retry_count}, backoff: {backoff}"
            )
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
            logger.warning(f"trying to send, but not connected calling _connect")

            await self._connect()

        await self.websocket.send(json.dumps(payload))

    async def subscribe(
        self,
        topic_key,
        handler: Callable,
        header: dict[str, str],
        body: dict[str, str],
    ):
        if self.receive_task is None:
            self.receive_task = asyncio.create_task(self.receive())
        # If the topic doesn't exist, create a list for handlers
        if topic_key not in self.subscriptions:
            self.subscriptions[topic_key] = []

        subscription_data = SubscriptionData(handler, header, body)
        # Add the handler to the list of handlers for this topic
        if not any(sub.handler is handler for sub in self.subscriptions[topic_key]):
            self.subscriptions[topic_key].append(subscription_data)

        # Start the receive loop if not already running for this topic
        if len(self.subscriptions[topic_key]) == 1:
            # Send a message to subscribe to the topic
            await self.send(header, body)

    async def resubscribe(self):
        for topic_key, subscription_datas in self.subscriptions.items():
            subscription_data = subscription_datas[0]
            header = subscription_data.header
            body = subscription_data.body

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
            self.subscriptions[topic_key] = [
                sub
                for sub in self.subscriptions[topic_key]
                if sub.handler is not handler
            ]

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
                    # logging.info(f"Message received: {message}")

                    response = json.loads(message)
                    topic_key = self.topic_extractor(response)
                    subscription_datas = self.subscriptions.get(topic_key, [])
                    try:
                        for subscription_data in subscription_datas:
                            handler = subscription_data.handler
                            await handler(response)
                    except Exception as e:
                        logger.exception(
                            f"An error occurred in websocket handlinga: {e}"
                        )

                except websockets.ConnectionClosedError as e:
                    logger.warning(f"Connection closed error, calling _connect, {e}")
                    await self._connect()
                    await self.resubscribe()
                except websockets.ConnectionClosed as e:
                    logger.warning(f"Connection closed, calling _connect, {e}")
                    await self._connect()
                    await self.resubscribe()

        except asyncio.CancelledError as e:
            logger.info("receive got CancelledError")
        except Exception as e:
            logger.exception(f"An unexpected error occurred in receive: {e}")
        finally:
            self.receive_task = None

    async def close(self):
        # TODO: maybe send close event to handlers

        self.subscriptions = {}
        if self.websocket and self.websocket.open:
            await self.websocket.close()
