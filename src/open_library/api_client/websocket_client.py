#!/usr/bin/env python3
import time
import asyncio
from dataclasses import dataclass
import json
import asyncio

from typing import Any, Dict, Optional, Callable, Awaitable
import logging
import websockets
from websockets.exceptions import ConnectionClosedOK

from open_library.logging.logging_filter import WebsocketLoggingFilter


ws_logger = logging.getLogger("websockets.client")
ws_filter = WebsocketLoggingFilter(60)  # Log once every 60 seconds for ping pong
ws_logger.addFilter(ws_filter)

logger = logging.getLogger(__name__)
ws_logger.setLevel(logging.INFO)


class CustomWebSocketClient(websockets.WebSocketClientProtocol):
    async def ping(self, data: Optional[Any] = None) -> Awaitable[None]:
        # for debug
        # logger.info("keepalive_ping")

        return await super().ping(data)


class NoPingPongFilter(logging.Filter):
    def filter(self, record):
        # Filter out ping/pong log messages
        return not ("ping" in record.getMessage() or "pong" in record.getMessage())


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

        self.websockets = []
        self.max_count = 10
        self.closed_websockets = []
        self.initial_reconnect_delay = 1
        self.reconnect_delay = 1
        self.max_reconnect_delay = 300
        self.last_connect_time = None

    async def connect(self):
        await self._connect()

    async def _connect(self):
        backoff = self.initial_delay

        if self.websocket is not None and self.websocket.open:
            logger.warning(f"trying to connect, but already connected")
            return

        if len(self.websockets) > self.max_count:
            logger.warning(f"trying to connect, but too many connections")
            return

        while self.retry_count != self.max_retries:
            logger.info(
                f"_connect, retry_count: {self.retry_count}, backoff: {backoff}"
            )
            try:
                self.websocket = await websockets.connect(
                    self.uri, create_protocol=CustomWebSocketClient
                )
                self.retry_count = 0  # reset retry count on successful connect
                await self.resubscribe()

                self.websockets.append(self.websocket)

                self.last_connect_time = time.monotonic()

                return
            except ConnectionRefusedError:
                self.retry_count += 1
                backoff = min(
                    self.initial_delay * (2**self.retry_count), self.max_delay
                )
                await asyncio.sleep(backoff)

        raise ConnectionRefusedError("Maximum retry count reached")

    async def _reconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.closed_websockets.append(self.websocket)
            try:
                self.websockets.remove(self.websocket)
            except:
                logger.warning("websockets remove fail")

        if self.last_connect_time is None:
            logger.warning(f"reconnect without first connecting")
            return

        time_since_last_reconnect = time.monotonic() - self.last_connect_time
        if time_since_last_reconnect < self.reconnect_delay:
            await asyncio.sleep(self.reconnect_delay - time_since_last_reconnect)

        # Delay in seconds
        await self._connect()

        if time_since_last_reconnect > self.reconnect_delay * 2:
            self.reconnect_delay = self.initial_reconnect_delay
        else:
            self.reconnect_delay = min(
                self.reconnect_delay * 2, self.max_reconnect_delay
            )

    async def send(self, header, body):
        header = header or {}
        body = body or {}
        access_token = await self.token_manager.get_access_token()

        header_updated = dict(token=access_token) | header

        payload = {"header": header_updated, "body": body}

        if self.websocket is None or not self.websocket.open:
            logger.warning(f"trying to send, but not connected calling _connect")

            await self._connect()

        logger.info(f"websocket send, header: {header}, body: {body}")

        try:
            await self.websocket.send(json.dumps(payload))
        except websockets.ConnectionClosedOK:
            logger.warning(f"ConnectionClosedOK")
            await self._reconnect()
        except websockets.ConnectionClosedError:
            logger.warning(f"send ConnectionClosedError")
            await self._reconnect()
        except websockets.ConnectionClosed as e:
            logger.warning(f"Connection closed, {e}")

    async def subscribe(
        self,
        topic_key,
        handler: Callable,
        header: dict[str, str],
        body: dict[str, str],
    ):
        logger.info(f"subscribe, topic_key: {topic_key}")
        if self.websocket is None or not self.websocket.open:
            await self._connect()

        if self.receive_task is None:
            self.receive_task = asyncio.create_task(self.receive())
        # If the topic doesn't exist, create a list for handlers
        if topic_key not in self.subscriptions:
            self.subscriptions[topic_key] = []

        subscription_data = SubscriptionData(handler, header, body)
        # Add the handler to the list of handlers for this topic
        if not any(sub.handler == handler for sub in self.subscriptions[topic_key]):
            self.subscriptions[topic_key].append(subscription_data)

        if True or len(self.subscriptions[topic_key]) == 1:
            # Send a message to subscribe to the topic
            await self.send(header, body)

    async def resubscribe(self):
        for topic_key, subscription_datas in self.subscriptions.items():
            logger.info(f"resubscribe, topic_key: {topic_key}")

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
                            f"An error occurred in websocket handling: {e}"
                        )
                except ConnectionClosedOK:
                    logger.warning(f"ConnectionClosedOK")
                    await self._reconnect()
                except websockets.ConnectionClosedError as e:
                    logger.warning(f"Connection closed error, calling _connect, {e}")
                    await self._reconnect()
                except websockets.ConnectionClosed as e:
                    logger.warning(f"Connection closed, calling _connect, {e}")
                    await self._reconnect()

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
