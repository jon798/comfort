import asyncio  # noqa: D104
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PIN, CONF_PORT
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_platform  # noqa: F401

from .const import DOMAIN, EVENT_MESSAGE

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):  # noqa: ANN201
    """Set up Comfort Integration from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    pin = entry.data[CONF_PIN]

    client = TCPClient(hass, host, port, pin, entry.entry_id)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    await client.connect()

    async def handle_send_message(call: ServiceCall):  # noqa: ANN202
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


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):  # noqa: ANN201
    """Unload a config entry."""
    client = hass.data[DOMAIN].pop(entry.entry_id, None)
    if client:
        await client.stop()
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return True


class TCPClient:
    """Persistent TCP connection with listener, reconnect, and event firing."""

    def __init__(  # noqa: ANN204, D107
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

    async def connect(self):  # noqa: ANN201
        """Connect and start listening."""
        while not self._stopping:
            try:
                self.listener_task = asyncio.create_task(self.listen())

                _LOGGER.info("Connecting to %s:%s", self.host, self.port)
                self.reader, self.writer = await asyncio.open_connection(
                    self.host, self.port
                )
                _LOGGER.info("Connected to %s:%s", self.host, self.port)

                self.writer.write(("\x03LI" + self.pin + "\r").encode())
                _LOGGER.info("Sent login: " + "\x03LI" + self.pin + "\r")  # noqa: G003

                # get security mode
                self.writer.write("\x03M?\r)".encode())
                _LOGGER.info("Sent get security mode")
                # get all zone input states
                self.writer.write("\x03Z?\r".encode())
                _LOGGER.info("Sent get all input states")

                return  # noqa: TRY300
            except Exception as e:  # noqa: BLE001
                _LOGGER.warning("Connection failed: %s. Retrying in 5s...", e)
                await asyncio.sleep(5)

    async def listen(self):  # noqa: ANN201
        """Listen for incoming messages and fire events + update entities."""
        try:
            while not self._stopping:
                data = await self.reader.readuntil(b"\r")  # type: ignore  # noqa: PGH003
                if not data:
                    _LOGGER.warning("Connection closed by remote host")
                    break
                msg = data.decode(errors="ignore").strip()
                if msg:
                    _LOGGER.info("Received message: %s", msg)
                    # Fire Home Assistant event
                    self.hass.bus.async_fire(EVENT_MESSAGE, {"message": msg})
                    # Notify entities
                    self.hass.bus.async_fire(
                        f"{EVENT_MESSAGE}_update",
                        {"entry_id": self.entry_id, "message": msg},
                    )
                if msg[1:3] == "Z?":
                    _LOGGER.info("Number of inputs: " + str((len(msg) - 3) * 4))
                if msg[1:3] == "LU":
                    _LOGGER.info("User logged in: " + msg[4:5])

        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOGGER.exception("Error in TCP listener: %s", e)  # noqa: TRY401
        finally:
            await self.schedule_reconnect()

    async def schedule_reconnect(self):  # noqa: ANN201
        """Attempt reconnect after delay."""
        if self._stopping:
            return
        _LOGGER.info("Reconnecting in 5 seconds...")
        await asyncio.sleep(5)
        await self.connect()

    async def send_message(self, message: str):  # noqa: ANN201
        """Send a message to the device."""
        if not self.writer:
            _LOGGER.warning("No active connection; reconnecting...")
            await self.connect()
        try:
            self.writer.write((message + "\n").encode())  # type: ignore  # noqa: PGH003
            await self.writer.drain()  # type: ignore  # noqa: PGH003
            _LOGGER.debug("Message sent: %s", message)
        except Exception as e:
            _LOGGER.exception("Failed to send message: %s", e)  # noqa: TRY401
            await self.schedule_reconnect()

    async def stop(self):  # noqa: ANN201
        """Stop listener and close connection."""
        self._stopping = True
        if self.listener_task:
            self.listener_task.cancel()
        if self.writer:
            self.writer.close()
            try:  # noqa: SIM105
                await self.writer.wait_closed()
            except Exception:  # noqa: BLE001, S110
                pass
        _LOGGER.info("TCP client stopped")
