import asyncio
import logging

# from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from .const import DOMAIN
from .comfortsys import ComfortSystem

from . import comfort

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.BINARY_SENSOR]

type ComfortConfigEntry = ConfigEntry[comfort.ComfortSystem]


async def async_setup_entry(hass: HomeAssistant, entry: ComfortConfigEntry):
    """Set up Comfort from a config entry."""
    entry.runtime_data = comfort.ComfortSystem(
        hass,
        entry.data["Login PIN"],
        entry.data["Comfort IP Address"],
        entry.data["Comfort TCP Port"],
        entry.data["Comfort Timeout"],
        entry.data["Retry Interval"],
        entry.data["Receive Buffer Size"],
        entry.data["System Name"],
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok
