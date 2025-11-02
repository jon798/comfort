"""Adds config flow for Comfort."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.helpers import selector

from .const import DOMAIN  # pylint:disable=unused-import

from custom_components.comfort.archive.zcomfortsys import ComfortSystem


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            "Login PIN",
            default=("6014"),
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            ),
        ),
        vol.Required(
            "Comfort IP Address",
            default=("192.168.4.205"),
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            ),
        ),
        vol.Required(
            "Comfort TCP Port",
            default=(1001),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                step=1,
                min=1,
                max=65535,
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Required(
            "Comfort Timeout",
            default=(30),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                step=1,
                min=10,
                max=240,
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Required(
            "Retry Interval",
            default=(5),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                step=1,
                min=1,
                max=30,
                mode=selector.NumberSelectorMode.BOX,
            ),
        ),
        vol.Required(
            "Receive Buffer Size",
            default=(4096),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                step=1024,
                min=1024,
                max=8192,
                mode=selector.NumberSelectorMode.SLIDER,
            ),
        ),
        vol.Required(
            "System Name",
            default=("Comfort Alarm"),
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            ),
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[Any, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.

    # This is a simple example to show an error in the UI for a short hostname
    # The exceptions are defined at the end of this file, and are used in the
    # `async_step_user` method below.
    if len(data["Comfort IP Address"]) < 3:
        raise InvalidHost

    comfort = ComfortSystem(
        hass,
        data["host"],
        data["port"],
        data["pin"],
        data["Comfort Timeout"],
        data["Retry Interval"],
        data["Receive Buffer Size"],
        data["System Name"],
    )
    # The dummy hub provides a `test_connection` method to ensure it's working
    # as expected
    # result = await comfort.test_connection()
    # if not result:
    # If there is an error, raise an exception to notify HA that there was a
    # problem. The UI will also show there was a problem
    # raise CannotConnect

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
    print("System name:", comfort.name)  # noqa: T201

    return {"title": "Comfort Alarm"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Comfort Integration."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                # The error string is set here, and should be translated.
                # This example does not currently cover translations, see the
                # comments on `DATA_SCHEMA` for further details.
                # Set the error on the `host` field, not the entire form.
                errors["host"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def async_step_reconfigure(self, user_input=None):
        if user_input is not None:
            info = await validate_input(self.hass, user_input)
            # await self.async_set_unique_id(user_id)
            # self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )
        return self.async_show_form(step_id="reconfigure", data_schema=DATA_SCHEMA)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
