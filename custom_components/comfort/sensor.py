from homeassistant.helpers.entity import Entity


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the sensor platform."""
    sensor = SocketClientSensor()
    async_add_entities([sensor])

    async def handle_message(event):
        data = event.data.get("data")
        sensor.set_state(data)
        await sensor.async_update_ha_state()

    hass.bus.async_listen("socket_client_message", handle_message)


class SocketClientSensor(Entity):
    """Representation of a socket client sensor."""

    def __init__(self):
        self._state = "Waiting"
        self._attr_name = "Socket Client Sensor"

    @property
    def state(self):
        return self._state

    def set_state(self, value):
        self._state = value
