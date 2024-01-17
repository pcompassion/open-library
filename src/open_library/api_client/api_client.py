#!/usr/bin/env python3
import httpx
import requests
import time
import asyncio
from typing import Any, Dict, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from open_library.asynch.util import periodic_wrapper

import logging

logger = logging.getLogger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

httpcore_logger = logging.getLogger("httpcore")
httpcore_logger.setLevel(logging.WARNING)


class TokenManager:
    # periodic proactive token refreshing
    def __init__(
        self,
        client: httpx.AsyncClient,
        token_url: str,
        client_id: str,
        client_secret: str,
    ):
        self.client = client
        self.token_url: str = token_url
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.access_token: Optional[str] = None
        self.refresh_deadline: datetime = datetime.utcnow()
        self.expiry_time: datetime = datetime.utcnow()
        self.task = None

    def start_refresh_task(self):
        PERIOD_CHECK_MIN = 60  # 1 hour

        if self.task is None:
            self.task = asyncio.create_task(
                periodic_wrapper(60 * PERIOD_CHECK_MIN, self.refresh_token)
            )

    async def get_access_token(self, force_refresh=False) -> Optional[str]:
        if self.is_near_expiration() or force_refresh:
            await self.refresh_token()
        return self.access_token

    async def refresh_token(self) -> None:
        headers = {"content-type": "application/x-www-form-urlencoded"}

        response = await self.client.post(
            self.token_url,
            headers=headers,
            params={
                "appkey": self.client_id,
                "appsecretkey": self.client_secret,
                "grant_type": "client_credentials",
                "scope": "oob",
            },
        )
        data: Dict[str, Any] = response.json()

        new_token = data.get("access_token", None)
        if new_token is None:
            logger.warning(f"no new token: {data}")
            raise Exception(f"no new token: {data}")

        logger.info(
            f"new_token: {new_token}, self: {id(self)}, client: {self.client_id}"
        )

        if self.access_token != data["access_token"]:
            logger.info(f"I have renewed token: {self.access_token}, new: {new_token}")

        self.access_token = data["access_token"]
        self.expires_in = data["expires_in"]
        self.token_acquired_at = datetime.utcnow()

        self.expiry_time = self.token_acquired_at + timedelta(
            seconds=data["expires_in"]
        )
        self.refresh_deadline = self.expiry_time - timedelta(seconds=300)

    def stop_refreshing(self) -> None:
        # Call this method when you want to stop the automatic token refreshing.
        if self.task:
            self.task.cancel()

    def is_near_expiration(self, threashold=300) -> bool:
        if self.access_token is None:
            return True

        return datetime.utcnow() + timedelta(seconds=threashold) > self.expiry_time


class ApiClient:
    # ebest doesn't have refresh token.. meantime we will use custom api client to handle token refresh
    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        min_interval_sec: float = 0.5,
        should_refresh_token_func: Callable[[httpx.Response], bool] | None = None,
    ):
        self.client = httpx.AsyncClient(verify=False, timeout=10)
        self.token_manager = TokenManager(
            self.client, token_url, client_id, client_secret
        )

        self.token_url: str = token_url
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.min_interval_sec = min_interval_sec

        self.last_request_time = None
        self.should_refresh_token_func = should_refresh_token_func

    async def request(
        self, url: str, method: str = "GET", **kwargs: Any
    ) -> httpx.Response:
        # Proactive token refreshing
        if self.token_manager.is_near_expiration():
            await self.token_manager.refresh_token()

        access_token = await self.token_manager.get_access_token()

        headers: Dict[str, str] = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {access_token}"
        kwargs["headers"] = headers

        response = await self.client.request(method, url, **kwargs)

        # Reactive token refreshing
        if response.status_code != 200:
            logger.warning(f"no good {response.status_code}")

            if (
                self.should_refresh_token_func is not None
                and self.should_refresh_token_func(response)
            ):
                logger.warning(f"refreshing token, response: {response}")
                access_token = await self.token_manager.get_access_token(
                    force_refresh=True
                )
                headers["Authorization"] = f"Bearer {access_token}"
                response = await self.client.request(method, url, **kwargs)

        return response

    def get_token_manager(self):
        return self.token_manager


class ApiResponse:
    def __init__(
        self,
        success,
        raw_data,
        headers,
        exchange_api_code,
        data_field_name=None,
        error_code=None,
        default_data_type=list,
    ):
        self.success = success
        self.raw_data = raw_data
        self.headers = headers
        self.data_field_name = data_field_name
        self.error_code = error_code
        self.default_data_type = default_data_type
        self.exchange_api_code = exchange_api_code

    @property
    def data(self):
        return self.raw_data.get(self.data_field_name, self.default_data_type())
