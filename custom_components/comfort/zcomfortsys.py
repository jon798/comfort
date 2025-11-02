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

from .zconst import DOMAIN

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

q = queue.SimpleQueue()

connections = {}


class ComfortSystem:
    """Comfort Alarm system interface."""

    manufacturer = "Cytech"


async def __init__(
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
    self.hass = hass
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

    reader, writer = await asyncio.open_connection(name, port)
    _LOGGER.info("Connected to %s:%s", name, port)
    print("Connected to %s:%s", name, port)
    connections[DOMAIN] = (reader, writer)
    writer.write(("\x03LI" + pin + "\r").encode())
    print("Sent login")

    async def listen_for_messages():
        """Background task to listen for unsolicited messages from the device."""
        _LOGGER.info("Starting background listener for TCP messages")
        print("Starting background listener for TCP messages")
        try:
            while True:
                data = await reader.readuntil(b"\r")
                if not data:
                    _LOGGER.warning("TCP connection closed by remote host")
                    break
                message = data.decode(errors="ignore").strip()
                if message:
                    _LOGGER.debug("Received unsolicited message: ", message)
                    print("Received unsolicited message: ", message)
                    hass.bus.async_fire(f"{DOMAIN}_message", {"message": message})
        except asyncio.CancelledError:
            _LOGGER.info("TCP listener task cancelled")
        except Exception as e:
            _LOGGER.exception("Error in TCP listener: %s", e)
        finally:
            writer.close()
            await writer.wait_closed()
            _LOGGER.info("TCP connection closed")

    listener_task = hass.loop.create_task(listen_for_messages())

    async def handle_send_message(call: ServiceCall):
        """Send a message to the TCP server."""
        message = call.data.get("message")
        if not message:
            _LOGGER.warning("No message provided in service call")
            return

        reader_writer = connections.get(DOMAIN)
        if not reader_writer:
            _LOGGER.error("No active TCP connection")
            return

        _, writer = reader_writer
        try:
            writer.write((message + "\n").encode())
            await writer.drain()
            _LOGGER.debug("Message sent: %s", message)
            print("Message sent: %s", message)
        except Exception as e:
            _LOGGER.exception("Failed to send message: %s", e)

    hass.services.async_register(DOMAIN, "send_message", handle_send_message)

    async def stop_connection(event):
        """Stop background listener and close connection when HA stops."""
        _LOGGER.info("Shutting down TCP integration")
        listener_task.cancel()
        try:
            await listener_task
        except asyncio.CancelledError:
            pass
            writer.close()
            await writer.wait_closed()

    hass.bus.async_listen_once("homeassistant_stop", stop_connection)
