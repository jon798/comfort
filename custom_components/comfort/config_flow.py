import voluptuous as vol  # noqa: D100
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_BUFFER_SIZE,
    CONF_HOST,
    CONF_PIN,
    CONF_PORT,
    CONF_RETRY_INTERVAL,
    CONF_SYSTEM_NAME,
    CONF_TIMEOUT,
    DOMAIN,
)

jonschema = vol.Schema(
    {
        vol.Required(
            CONF_PIN,
            default=("6014"),
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            ),
        ),
        vol.Required(
            CONF_HOST,
            default=("192.168.4.205"),
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            ),
        ),
        vol.Required(
            CONF_PORT,
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
            CONF_TIMEOUT,
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
            CONF_RETRY_INTERVAL,
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
            CONF_BUFFER_SIZE,
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
            CONF_SYSTEM_NAME,
            default=("Comfort Alarm"),
        ): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT,
            ),
        ),
    }
)


class ComfortConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Comfort Integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):  # noqa: ANN001, ANN201, D102
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_SYSTEM_NAME], data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=jonschema, errors=errors
        )

    async def async_step_reconfigure(self, user_input=None):  # noqa: ANN001, ANN201, D102
        if user_input is not None:
            # info = await validate_input(self.hass, user_input)  # noqa: ERA001
            # await self.async_set_unique_id(user_id)  # noqa: ERA001
            # self._abort_if_unique_id_mismatch()  # noqa: ERA001
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )
        return self.async_show_form(step_id="reconfigure", data_schema=jonschema)
