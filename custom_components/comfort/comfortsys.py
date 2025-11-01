"""Comfort Alam Interface."""

from __future__ import annotations

# In a real implementation, this would be in an external library that's on PyPI.
# The PyPI package needs to be included in the `requirements` section of manifest.json
# See https://developers.home-assistant.io/docs/creating_integration_manifest
# for more information.

from os import wait
import random
import socket
import asyncio
import time
import threading
import queue
import logging

_LOGGER = logging.getLogger(__name__)

from homeassistant.core import callback

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

q = queue.SimpleQueue()


class ComfortSystem:
    """Comfort Alarm system interface."""

    manufacturer = "Cytech"

    async def __init__(
        self,
        hass: HomeAssistant,
        pin: str,
        ip: str,
        port: int,
        # comforttimeout: int,
        # retry: int,
        # buffer: int,
        # name: str,
    ) -> None:
        """Init Comfort Alarm."""
        self.hass = hass
        # self.name = name
        self.pin = pin
        self.ip = ip
        self.port = int(port)
        # self.comforttimeout = int(comforttimeout)
        # self.retry = int(retry)
        # self.buffer = int(buffer)
        # self.id = name.lower()
        # Create the devices that are part of this hub.
        # In a real implementation, this would query the hub to find the devices.
        print("connecting to " + ip + " on port " + str(int(port)))

        async def connect_to_server():
            while True:
                try:
                    _LOGGER.info("Connecting to %s:%s...", ip, port)
                    reader, writer = await asyncio.open_connection(ip, port)
                    _LOGGER.info("Connected to %s:%s", ip, port)
                    writer.write(("\x03LI" + pin + "\r").encode())
                    print("Sent:", ("\x03LI" + pin + "\r").encode())

                    while data := await reader.readline():
                        message = data.decode().strip()
                        _LOGGER.info("Received: %s", message)
                        print("Received: %s", message)

                        # hass.data[DOMAIN]["messages"].append(message)
                        # hass.bus.async_fire(f"{DOMAIN}_message", {"data": message})
                except Exception as e:
                    _LOGGER.error("Socket client error: %s", e)
                    _LOGGER.info("Reconnecting in 10 seconds...")
                await asyncio.sleep(10)

        hass.loop.create_task(connect_to_server())
        return None
