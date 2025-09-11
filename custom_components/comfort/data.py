"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry  # ignore
    from homeassistant.loader import Integration  # ignore

    from .api import ComfortApiClient
    from .coordinator import ComfortDataUpdateCoordinator


type ComfortConfigEntry = ConfigEntry[ComfortData]


@dataclass
class ComfortData:
    """Data for the Comfort integration."""

    pin: str
    ip: str
    port: int
    timeout: int
    retry: int
    # client: ComfortApiClient
    coordinator: ComfortDataUpdateCoordinator
    integration: Integration
