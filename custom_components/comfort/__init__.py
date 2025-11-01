import asyncio
import logging
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, ServiceCall
from .const import DOMAIN, CONF_HOST, CONF_PORT

_LOGGER = logging.getLogger(__name__)

connections = {}


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the TCP integration from configuration.yaml."""
    conf = config.get(DOMAIN)
    if conf is None:
        _LOGGER.error("No configuration found for %s", DOMAIN)
        return False

    host = conf.get(CONF_HOST)
    port = conf.get(CONF_PORT)

    reader, writer = await asyncio.open_connection(host, port)
    _LOGGER.info("Connected to %s:%s", host, port)
    print("Connected to %s:%s", host, port)
    connections[DOMAIN] = (reader, writer)
    writer.write(("\x03LI6014\r").encode())
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
                    _LOGGER.debug("Received unsolicited message: %s", message)
                    print("Received unsolicited message: %s", message)
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

    return True
