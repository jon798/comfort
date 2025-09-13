"""Adds config flow for Comfort."""

from __future__ import annotations

from ipaddress import ip_address
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.core import HomeAssistant

from comfort import Comfort

from .const import (
    BUFFER_SIZE,
    COMFORT_IP,
    COMFORT_PIN,
    COMFORT_PORT,
    COMFORT_RETRY,
    COMFORT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        ("pin"): str,
        ("ip"): str,
        ("comfortport"): int,
        ("comforttimeout"): int,
        ("retry"): int,
        ("buffer"): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.

    # This is a simple example to show an error in the UI for a short hostname
    # The exceptions are defined at the end of this file, and are used in the
    # `async_step_user` method below.
    if len(data["ip"]) < 3:
        raise InvalidHost

    comfort = Comfort(
        hass,
        data["pin"],
        data["ip"],
        data["port"],
        data["comforttimeout"],
        data["retry"],
        data["buffer"],
        data["name"],
    )
    # The dummy hub provides a `test_connection` method to ensure it's working
    # as expected
    result = await comfort.test_connection()
    if not result:
        # If there is an error, raise an exception to notify HA that there was a
        # problem. The UI will also show there was a problem
        raise CannotConnect

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    # "Title" is what is displayed to the user for this hub device
    # It is stored internally in HA as part of the device config.
    # See `async_step_user` below for how this is used

    print("Comfort Login pin:", comfort.pin)  # noqa: T201
    print("Comfort IP Address:", comfort.ip)  # noqa: T201
    print("Comfort TCP Port:", comfort.port)  # noqa: T201
    print("Timeout:", comfort.comforttimeout)  # noqa: T201
    print("Retry delay:", comfort.retry)  # noqa: T201
    print("Receive buffer size:", comfort.buffer)  # noqa: T201

    return {"title": "Comfort Alarm"}


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
