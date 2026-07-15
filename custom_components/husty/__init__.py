from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import HustyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Husty from a config entry."""

    coordinator = HustyCoordinator(
        hass,
        entry.data["email"],
        entry.data["password"],
        entry.data["device_id"],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        [
            "sensor",
            "binary_sensor",
        ],
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload Husty."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        [
            "sensor",
            "binary_sensor",
        ],
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok