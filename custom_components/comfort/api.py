"""Sample API Client."""

from __future__ import annotations

import socket
from typing import Any

import select
import math
import time
import datetime
import threading
from datetime import timedelta

import async_timeout

from custom_components.comfort.const import COMFORT_RETRY

BUFFER_SIZE=4096


class ComfortApiClientError(Exception):
    """Exception to indicate a general API error."""


class ComfortApiClientCommunicationError(
    ComfortApiClientError,
):
    """Exception to indicate a communication error."""





class ComfortApiClient:
    """Sample API Client."""

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
        self._port = math.floor(port)
        self.timeout = timeout
        self.retry = retry
        self.connected=False
        # self.comfortsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("connecting to " + ip + " " + str(port))
        #self.comfortsock.connect((ip, math.floor(port)))

    async def readlines(self):
