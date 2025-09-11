"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import ComfortDataUpdateCoordinator


class ComfortEntity(CoordinatorEntity[ComfortDataUpdateCoordinator]):
    """ComfortEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: ComfortDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            name=coordinator.config_entry.title,
            manufacturer="Comfort",
            model="Jon's lovely Comfort Alarm",
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )
