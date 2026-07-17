"""Data update coordinator for Husty."""

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
    """Coordinate periodic updates from Husty."""

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

    async def _async_update_data(
        self,
    ) -> dict[str, Any]:
        """Fetch current Husty data."""

        try:
            data = await self.api.async_get_device()

        except HustyAuthenticationError as err:
            raise ConfigEntryAuthFailed(
                str(err)
            ) from err

        except (
            HustyConnectionError,
            HustyInvalidResponseError,
        ) as err:
            raise UpdateFailed(
                str(err)
            ) from err

        metadata = data.get("metadata", {})

        _LOGGER.debug(
            "Odświeżono Husty: device_id=%s, last_updated=%s",
            data.get("deviceId"),
            metadata.get("lastUpdatedAt"),
        )

        return data
