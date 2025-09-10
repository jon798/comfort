"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import ComfortJAApiClient
    from .coordinator import ComfortJADataUpdateCoordinator


type ComfortJAConfigEntry = ConfigEntry[ComfortJAData]


@dataclass
class ComfortJAData:
    """Data for the Blueprint integration."""

    client: ComfortJAApiClient
    coordinator: ComfortJADataUpdateCoordinator
    integration: Integration
