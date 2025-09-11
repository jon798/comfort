"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import ComfortApiClient
    from .coordinator import ComfortDataUpdateCoordinator


type ComfortConfigEntry = ConfigEntry[ComfortData]


@dataclass
class ComfortData:
    """Data for the Comfort integration."""

    pin: str
    ip: str
    port: int
    client: ComfortApiClient
    coordinator: ComfortDataUpdateCoordinator
    integration: Integration
