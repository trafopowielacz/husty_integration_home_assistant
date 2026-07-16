"""Husty integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import HustyApiClient
from .const import (
    CONF_DEVICE_ID,
    CONF_EMAIL,
    CONF_PASSWORD,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import HustyCoordinator

type HustyConfigEntry = ConfigEntry[HustyCoordinator]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HustyConfigEntry,
) -> bool:
    """Set up Husty from a config entry."""

    api = HustyApiClient(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
        device_id=entry.data[CONF_DEVICE_ID],
    )

    coordinator = HustyCoordinator(
        hass=hass,
        config_entry=entry,
        api=api,
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

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

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if not unload_ok:
        return False

    coordinator = entry.runtime_data
    await coordinator.api.async_close()

    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)

    if not hass.data.get(DOMAIN):
        hass.data.pop(DOMAIN, None)

    return True
