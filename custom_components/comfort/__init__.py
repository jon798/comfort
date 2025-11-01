import asyncio
import logging

from homeassistant.core import HomeAssistant

DOMAIN = "comfort"
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the comfort integration."""
    # You can define this in configuration.yaml (see below)
    conf = config.get(DOMAIN, {})
    host = "192.168.4.205"
    port = 1001
    pin = "6014"

    hass.data[DOMAIN] = {"messages": []}

    async def connect_to_server():
        while True:
            try:
                _LOGGER.info("Connecting to %s:%s...", host, port)
                reader, writer = await asyncio.open_connection(host, port)
                _LOGGER.info("Connected to %s:%s", host, port)
                writer.write(("\x03LI" + pin + "\r").encode())

                while data := await reader.readline():
                    message = data.decode().strip()
                    _LOGGER.info("Received: %s", message)
                    hass.data[DOMAIN]["messages"].append(message)
                    hass.bus.async_fire(f"{DOMAIN}_message", {"data": message})
            except Exception as e:
                _LOGGER.error("Socket client error: %s", e)
                _LOGGER.info("Reconnecting in 10 seconds...")
                await asyncio.sleep(10)

    hass.loop.create_task(connect_to_server())
    return True
