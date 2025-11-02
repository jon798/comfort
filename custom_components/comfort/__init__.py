import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import entity_platform
from .const import DOMAIN, EVENT_MESSAGE

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Comfort Integration from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    client = TCPClient(hass, host, port, entry.entry_id)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    await client.connect()

    async def handle_send_message(call: ServiceCall):
        """Send message service."""
        msg = call.data.get("message")
        if not msg:
            _LOGGER.warning("No message provided in service call")
            return
        await client.send_message(msg)

    hass.services.async_register(DOMAIN, "send_message", handle_send_message)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(
        hass.bus.async_listen_once("homeassistant_stop", lambda _: client.stop())
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    client = hass.data[DOMAIN].pop(entry.entry_id, None)
    if client:
        await client.stop()
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return True


class TCPClient:
    """Persistent TCP connection with listener, reconnect, and event firing."""

    def __init__(
        self, hass: HomeAssistant, host: str, port: int, pin: str, entry_id: str
    ):
        self.hass = hass
        self.host = host
        self.port = int(port)
        self.pin = pin
        self.entry_id = entry_id
        self.reader = None
        self.writer = None
        self.listener_task = None
        self._stopping = False

    async def connect(self):
        """Connect and start listening."""
        while not self._stopping:
            try:
                _LOGGER.info("Connecting to %s:%s", self.host, self.port)
                self.reader, self.writer = await asyncio.open_connection(
                    self.host, self.port
                )
                _LOGGER.info("Connected to %s:%s", self.host, self.port)
                self.writer.write(("\x03LI" + self.pin + "\r").encode())
                _LOGGER.info("Sent login: " + "\x03LI" + self.pin + "\r")
                self.listener_task = asyncio.create_task(self.listen())
                return
            except Exception as e:
                _LOGGER.warning("Connection failed: %s. Retrying in 5s...", e)
                await asyncio.sleep(5)

    async def listen(self):
        """Listen for incoming messages and fire events + update entities."""
        try:
            while not self._stopping:
                data = await self.reader.readuntil(b"\r")
                if not data:
                    _LOGGER.warning("Connection closed by remote host")
                    break
                msg = data.decode(errors="ignore").strip()
                if msg:
                    _LOGGER.debug("Received message: %s", msg)
                    # Fire Home Assistant event
                    self.hass.bus.async_fire(EVENT_MESSAGE, {"message": msg})
                    # Notify entities
                    self.hass.bus.async_fire(
                        f"{EVENT_MESSAGE}_update",
                        {"entry_id": self.entry_id, "message": msg},
                    )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.exception("Error in TCP listener: %s", e)
        finally:
            await self.schedule_reconnect()

    async def schedule_reconnect(self):
        """Attempt reconnect after delay."""
        if self._stopping:
            return
        _LOGGER.info("Reconnecting in 5 seconds...")
        await asyncio.sleep(5)
        await self.connect()

    async def send_message(self, message: str):
        """Send a message to the device."""
        if not self.writer:
            _LOGGER.warning("No active connection; reconnecting...")
            await self.connect()
        try:
            self.writer.write((message + "\n").encode())
            await self.writer.drain()
            _LOGGER.debug("Message sent: %s", message)
        except Exception as e:
            _LOGGER.exception("Failed to send message: %s", e)
            await self.schedule_reconnect()

    async def stop(self):
        """Stop listener and close connection."""
        self._stopping = True
        if self.listener_task:
            self.listener_task.cancel()
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass
        _LOGGER.info("TCP client stopped")
