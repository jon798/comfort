"""Adds config flow for Blueprint."""

from __future__ import annotations
from tkinter import messagebox

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from slugify import slugify

from .api import (
    ComfortApiClient,
    ComfortApiClientAuthenticationError,
    ComfortApiClientCommunicationError,
    ComfortApiClientError,
)
from .const import DOMAIN, LOGGER


class ComfortFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Comfort Integration."""

    VERSION = 1

    async def async_step_system(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._system_details(
                    pin=user_input[CONF_USERNAME],
                )
            finally:
                await self.async_set_unique_id(
                    ## Do NOT use this in production code
                    ## The unique_id should never be something that can change
                    ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                    unique_id=slugify(user_input[CONF_USERNAME])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="system",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    # vol.Required(CONF_PASSWORD): selector.TextSelector(
                    #     selector.TextSelectorConfig(
                    #         type=selector.TextSelectorType.PASSWORD,
                    #     ),
                    # ),
                },
            ),
            errors=_errors,
        )

    async def _system_details(self, pin: str) -> None:
        """Get system details."""
        print("Comfort System Details For now...",,, pin
              )
