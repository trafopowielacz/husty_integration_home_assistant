from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
    async_add_entities
):

    coordinator = (
        hass.data[DOMAIN][entry.entry_id]
    )


    async_add_entities([

        HustyValveSensor(
            coordinator
        ),

        HustyOnlineSensor(
            coordinator
        ),

    ])



class HustyValveSensor(
    CoordinatorEntity,
    BinarySensorEntity
):

    _attr_name = (
        "Husty Zawór zamknięty"
    )

    _attr_icon = (
        "mdi:valve"
    )


    @property
    def unique_id(self):

        return "husty_valve_closed"


    @property
    def is_on(self):

        data = (
            self.coordinator.data[1]
            ["result"]
            ["data"]
            ["json"]
        )

        state = (
            data["core"]
            .get(
                "leakageShutoffValveState"
            )
        )

        return state == 2



class HustyOnlineSensor(
    CoordinatorEntity,
    BinarySensorEntity
):

    _attr_name = (
        "Husty Online"
    )

    _attr_icon = (
        "mdi:cloud-check"
    )


    @property
    def is_on(self):

        data = (
            self.coordinator.data[1]
            ["result"]
            ["data"]
            ["json"]
        )

        return (
            data.get("status")
            == "online"
        )
