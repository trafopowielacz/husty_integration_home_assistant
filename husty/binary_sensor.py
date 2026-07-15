from homeassistant.components.binary_sensor import (
    BinarySensorEntity
)

from .const import DOMAIN



async def async_setup_entry(
    hass,
    entry,
    async_add_entities
):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            HustyOnline(coordinator)
        ]
    )



class HustyOnline(
    BinarySensorEntity
):

    _attr_name = "Husty Online"


    def __init__(
        self,
        coordinator
    ):

        self.coordinator = coordinator


    @property
    def is_on(self):

        return (
            self.coordinator.data[1]
            ["result"]
            ["data"]
            ["json"]
            ["status"]
            ==
            "online"
        )