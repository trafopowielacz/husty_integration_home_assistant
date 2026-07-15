from .const import DOMAIN
from .coordinator import HustyCoordinator


async def async_setup_entry(hass, entry):

    coordinator = HustyCoordinator(
        hass,
        entry.data["email"],
        entry.data["password"],
        entry.data["device_id"],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(
        DOMAIN,
        {}
    )[entry.entry_id] = coordinator


    await hass.config_entries.async_forward_entry_setups(
        entry,
        [
            "sensor",
            "binary_sensor"
        ]
    )

    return True