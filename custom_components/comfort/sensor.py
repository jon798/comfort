from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from .zconst import DOMAIN, EVENT_MESSAGE


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up message sensor."""
    host = entry.data[CONF_HOST]
    sensor = ComfortMessageSensor(entry.entry_id, host)
    async_add_entities([sensor])

    # Listen for incoming message updates
    @callback
    def handle_message_event(event):
        data = event.data
        if data.get("entry_id") == entry.entry_id:
            sensor.update_message(data.get("message"))

    hass.bus.async_listen(f"{EVENT_MESSAGE}_update", handle_message_event)


class ComfortMessageSensor(SensorEntity):
    """Sensor showing the last message received."""

    _attr_name = "Last Message"
    _attr_icon = "mdi:message-text-outline"

    def __init__(self, entry_id, host):
        self._attr_unique_id = f"{entry_id}_last_message"
        self._attr_extra_state_attributes = {"host": host}
        self._state = None

    @property
    def state(self):
        return self._state

    @callback
    def update_message(self, msg: str):
        """Update sensor state when new message arrives."""
        self._state = msg
        self.async_write_ha_state()
