from homeassistant.components.sensor import SensorEntity  # noqa: D100
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

from custom_components.comfort.archive import binary_sensor

from .const import EVENT_MESSAGE


async def async_setup_entry(hass, entry, async_add_entities) -> None:  # noqa: ANN001
    """Set up input sensors."""
    host = entry.data[CONF_HOST]
    sensor = ComfortInputSensor(entry.entry_id, host)
    async_add_entities([binary_sensor])

    # Listen for incoming message updates
    @callback
    def handle_message_event(event) -> None:  # noqa: ANN001
        data = event.data
        if data.get("entry_id") == entry.entry_id:
            sensor.update_message(data.get("message"))

    hass.bus.async_listen(f"{EVENT_MESSAGE}_update", handle_message_event)


class ComfortInputSensor(SensorEntity):
    """Sensor showing the state of an input."""

    _attr_name = "State of Input"
    _attr_icon = "mdi:message-text-outline"

    def __init__(self, entry_id, host):  # noqa: ANN001, ANN204, D107
        self._attr_unique_id = f"{entry_id}_Input"
        # self._attr_extra_state_attributes = {"host": host}
        self._state = None

    @property
    def state(self):  # noqa: ANN201, D102
        return self._state

    @callback
    def update_message(self, msg: str):  # noqa: ANN201
        """Update sensor state when new message arrives."""
        self._state = msg
        self.async_write_ha_state()
