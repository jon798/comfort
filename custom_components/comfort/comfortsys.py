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

from homeassistant.core import callback

from typing import TYPE_CHECKING, Callable

from sqlalchemy import true

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

q = queue.SimpleQueue()


class ComfortSystem:
    """Comfort Alarm system interface."""

    manufacturer = "Cytech"

    def __init__(
        self,
        hass: HomeAssistant,
        pin: str,
        ip: str,
        port: int,
        comforttimeout: int,
        retry: int,
        buffer: int,
        name: str,
    ) -> None:
        """Init Comfort Alarm."""
        self._hass = hass
        self.name = name
        self.pin = pin
        self.ip = ip
        self.port = int(port)
        self.comforttimeout = int(comforttimeout)
        self.retry = int(retry)
        self.buffer = int(buffer)
        self.id = name.lower()
        # Create the devices that are part of this hub.
        # In a real implementation, this would query the hub to find the devices.

    #    self.inputs = [
    #            ComfortInput(f"{self._id}_1", f"{self._name} 1", self),
    #            ComfortInput(f"{self._id}_2", f"{self._name} 2", self),
    #            ComfortInput(f"{self._id}_3", f"{self._name} 3", self),

    #       self.others = []  # type: list[ComfortInput]
    #       self.online = True

    @property
    def hub_id(self) -> str:
        """ID for dummy hub."""
        return self.id

    async def test_connection(self) -> bool:
        """Test connectivity to the Dummy hub is OK."""
        await asyncio.sleep(1)
        return True


class ComfortInput:
    """Comfort Input device."""

    def __init__(self, inputid: str, name: str, comfort: ComfortSystem) -> None:
        """Init Comfort Input."""
        self._id = inputid
        self.hub = comfort
        self.name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()

        # Some static information about this device
        self.model = "PIR Input"

    @property
    def input_id(self) -> str:
        """Return ID for input."""
        return self._id

    async def delayed_update(self) -> None:
        """Publish updates, with a random delay to emulate interaction with device."""
        await asyncio.sleep(random.randint(1, 10))
        await self.publish_updates()

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register callback, called when input changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback: Callable[[], None]) -> None:
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changes for the relevant device.
    async def publish_updates(self) -> None:
        """Schedule call all registered callbacks."""
        # self._current_position = self._target_position
        for callback in self._callbacks:
            callback()


class ComfortLUUserLoggedIn(object):
    def __init__(self, datastr="", user=0):
        if datastr:
            self.user = int(datastr[2:4], 16)
        else:
            self.user = int(user)
