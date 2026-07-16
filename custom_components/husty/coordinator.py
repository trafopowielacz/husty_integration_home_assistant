"""Data coordinator for Husty."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    HustyApiClient,
    HustyAuthenticationError,
    HustyConnectionError,
    HustyInvalidResponseError,
)
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class HustyCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Coordinate Husty API updates."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: HustyApiClient,
    ) -> None:
        """Initialize the coordinator."""

        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            always_update=True,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the newest data from Husty."""

        try:
            data = await self.api.async_get_data()

        except HustyAuthenticationError as err:
            raise ConfigEntryAuthFailed(
                "Logowanie do Husty nie powiodło się"
            ) from err

        except (
            HustyConnectionError,
            HustyInvalidResponseError,
        ) as err:
            raise UpdateFailed(str(err)) from err

        device = data.get("device", {})
        metadata = device.get("metadata", {})

        _LOGGER.debug(
            "Odświeżono dane Husty. Urządzenie: %s, raport: %s",
            device.get("deviceId"),
            metadata.get("lastReportedAt"),
        )

        return data
