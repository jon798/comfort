from homeassistant import config_entries
import voluptuous as vol
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import selector
from .const import DOMAIN, DEFAULT_PORT


class ComfortConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Comfort Integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        schema = vol.Schema(
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

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
