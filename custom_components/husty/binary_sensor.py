from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN


BINARY_SENSORS = {

    "online": {
        "name": "Online",
        "path": [
            "metadata",
            "connectionState"
        ],
    },

    "regeneration": {
        "name": "Regeneracja aktywna",
        "path": [
            "core",
            "regenerationInProgress"
        ],
    },

    "shutoff_valve": {
        "name": "Zawór odcinający",
        "path": [
            "core",
            "leakageShutoffValveState"
        ],
    },

}



async def async_setup_entry(
    hass,
    entry,
    async_add_entities
):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            HustyBinarySensor(
                coordinator,
                key,
                data
            )

            for key, data in BINARY_SENSORS.items()
        ]
    )



class HustyBinarySensor(BinarySensorEntity):

    def __init__(
        self,
        coordinator,
        key,
        data
    ):

        self.coordinator = coordinator

        self.path = data["path"]

        self._attr_unique_id = (
            f"husty_{key}"
        )

        self._attr_name = (
            f"Husty {data['name']}"
        )

        self._attr_icon = (
            "mdi:valve"
            if key == "shutoff_valve"
            else "mdi:check-network"
        )



    @property
    def device_info(self):

        data = (
            self.coordinator.data[1]
            ["result"]
            ["data"]
            ["json"]
        )

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    data["deviceId"]
                )
            },

            name="Husty SaoCal 250 LE",

            manufacturer="Husty",

            model=data["core"]["model"],

            sw_version=data["core"]["version"],
        )



    @property
    def is_on(self):

        data = (
            self.coordinator.data[1]
            ["result"]
            ["data"]
            ["json"]
        )


        for item in self.path:

            data = data[item]


        if self.path[-1] == "connectionState":

            return data == "Connected"


        if self.path[-1] == "leakageShutoffValveState":

            return data == 0


        return bool(data)
