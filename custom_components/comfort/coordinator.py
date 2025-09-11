"""DataUpdateCoordinator for integration_blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    ComfortApiClient,
    ComfortApiClientAuthenticationError,
    ComfortApiClientError,
)

from .const import LOGGER as _LOGGER

if TYPE_CHECKING:
    from .data import ComfortConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class ComfortDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ComfortConfigEntry

    def __init__(self, hass, name, logger, config_entry, my_api) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="My thing in here",
            update_interval=None,
            always_update=True,
        )
        self.my_api = ComfortApiClient

    async def _async_update_data(self) -> Any:
        """Update data via library."""

    #  try:
    #      return await self.config_entry.runtime_data.client.async_get_data()
    #  except ComfortApiClientAuthenticationError as exception:
    #      raise ConfigEntryAuthFailed(exception) from exception
    #  except ComfortApiClientError as exception:
    #      raise UpdateFailed(exception) from exception
    pass
