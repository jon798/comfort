"""Adds config flow for Comfort."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from slugify import slugify

from .const import (
    BUFFER_SIZE,
    COMFORT_IP,
    COMFORT_PIN,
    COMFORT_PORT,
    COMFORT_RETRY,
    COMFORT_TIMEOUT,
    DOMAIN,
)


class ComfortFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            await self._system(user_input)

            await self.async_set_unique_id(
                ## Do NOT use this in production code
                ## The unique_id should never be something that can change
                ## https://developers.home-assistant.io/docs/config_entries_config_flow_handler#unique-ids
                unique_id=slugify(user_input[COMFORT_IP])
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Comfort Alarm",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        COMFORT_PIN,
                        default=(user_input or {}).get(COMFORT_PIN, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        COMFORT_IP,
                        default=(user_input or {}).get(COMFORT_IP, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        COMFORT_PORT,
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
                        COMFORT_TIMEOUT,
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
                        COMFORT_RETRY,
                        default=(5),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            step=1,
                            min=1,
                            max=240,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Required(
                        BUFFER_SIZE,
                        default=(4096),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            step=1024,
                            min=1024,
                            max=8192,
                            mode=selector.NumberSelectorMode.SLIDER,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _system(self, params: dict) -> None:
        """Validate system."""
        print("Comfort Login pin:", params[COMFORT_PIN])  # noqa: T201
        print("Comfort IP Address:", params[COMFORT_IP])  # noqa: T201
        print("Comfort TCP Port:", params[COMFORT_PORT])  # noqa: T201
        print("Timeout:", params[COMFORT_TIMEOUT])  # noqa: T201
        print("Retry delay:", params[COMFORT_RETRY])  # noqa: T201
        print("Receive buffer size:", params[BUFFER_SIZE])  # noqa: T201
