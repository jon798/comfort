"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import select
import time
import datetime
import threading
from datetime import timedelta


import aiohttp
import async_timeout


class ComfortApiClientError(Exception):
    """Exception to indicate a general API error."""


class ComfortApiClientCommunicationError(
    ComfortApiClientError,
):
    """Exception to indicate a communication error."""


class ComfortApiClientAuthenticationError(
    ComfortApiClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise ComfortApiClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class ComfortApiClient:
    """Sample API Client."""

    def login(self):
        self.comfortsock.sendall(("\x03LI" + self._pin + "\r").encode())

    def __init__(
        self,
        pin: str,
        ip: str,
        port: int,
        timeout: timedelta,
        retry: timedelta,
    ) -> None:
        """Initialize."""
        self._pin = pin
        self._ip = ip
        self._port = port
        self.timeout = timeout
        self.retry = retry
        while True:
            try:
                self.comfortsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("connecting to " + ip + " " + str(port))
                self.comfortsock.connect((ip, port))
                self.comfortsock.settimeout(timeout.seconds)
                self.login()
            except socket.error as v:
                # errorcode = v[0]
                print("socket error " + str(v))
                # raise
                print("lost connection to comfort, reconnecting...")
                time.sleep(retry.seconds)

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
        )

    async def async_set_title(self, value: str) -> Any:
        """Get data from the API."""
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"title": value},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                #    response = await self._session.request(
                #        method=method,
                #        url=url,
                #        headers=headers,
                #        json=data,
                #    )
                pass
            # _verify_response_or_raise(response)
            return  # await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise ComfortApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise ComfortApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise ComfortApiClientError(
                msg,
            ) from exception
