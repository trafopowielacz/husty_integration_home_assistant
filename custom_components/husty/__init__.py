"""Husty integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)

from .api import HustyApiClient
from .const import (
    CONF_API_KEY,
    DEVICE_URL,
    PLATFORMS,
    REQUEST_TIMEOUT,
)
from .coordinator import HustyCoordinator

HustyConfigEntry = ConfigEntry[HustyCoordinator]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HustyConfigEntry,
) -> bool:
    """Set up Husty from a config entry."""

    api_key = entry.data.get(CONF_API_KEY)

    if not isinstance(api_key, str) or not api_key:
        raise ConfigEntryAuthFailed(
            "Wymagany jest klucz API Husty"
        )

    session = async_get_clientsession(hass)

    api = HustyApiClient(
        session=session,
        api_key=api_key,
        device_url=DEVICE_URL,
        request_timeout=REQUEST_TIMEOUT,
    )

    coordinator = HustyCoordinator(
        hass=hass,
        config_entry=entry,
        api=api,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: HustyConfigEntry,
) -> bool:
    """Unload a Husty config entry."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
