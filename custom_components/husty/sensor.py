from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN


SENSORS = {

    "salt_level": {
        "name": "Sól",
        "path": [
            "core",
            "saltLevel1"
        ],
        "unit": "kg",
        "icon": "mdi:shaker",
    },


    "water_remaining": {
        "name": "Pozostała woda",
        "path": [
            "core",
            "waterSupply"
        ],
        "unit": "L",
        "icon": "mdi:water",
    },


    "water_remaining_percent": {
        "name": "Pozostała woda procent",
        "path": [
            "core",
            "waterSupplyPercent"
        ],
        "unit": "%",
        "icon": "mdi:water-percent",
    },


    "water_flow": {
        "name": "Przepływ wody",
        "path": [
            "core",
            "waterFlow"
        ],
        "unit": "L/min",
        "icon": "mdi:water-pump",
        "flow": True,
    },


    "water_today": {
        "name": "Zużycie wody dzisiaj",
        "path": [
            "core",
            "consumption",
            "today",
            "total"
        ],
        "unit": "L",
        "icon": "mdi:water",
        "total": True,
    },


    "water_month": {
        "name": "Zużycie wody miesiąc",
        "path": [
            "core",
            "consumption",
            "month",
            "total"
        ],
        "unit": "L",
        "icon": "mdi:calendar-month",
        "total": True,
    },


    "water_total": {
        "name": "Zużycie wody całkowite",
        "path": [
            "core",
            "consumption",
            "year",
            "total"
        ],
        "unit": "L",
        "icon": "mdi:water-sync",
        "total": True,
    },


    "regeneration_days": {
        "name": "Regeneracja za",
        "path": [
            "core",
            "remainingDaysToNextRegeneration"
        ],
        "unit": "dni",
        "icon": "mdi:calendar-refresh",
    },


    "salt_regenerations": {
        "name": "Pozostałe regeneracje z soli",
        "path": [
            "core",
            "saltRegenerationsLeft"
        ],
        "unit": None,
        "icon": "mdi:shaker-outline",
    },


    "last_connection": {
        "name": "Ostatnie połączenie",
        "path": [
            "metadata",
            "lastReportedAt"
        ],
        "unit": None,
        "icon": "mdi:lan-connect",
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
            HustySensor(
                coordinator,
                key,
                data
            )

            for key, data in SENSORS.items()
        ]
    )



class HustySensor(SensorEntity):

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
            data["icon"]
        )

        self._attr_native_unit_of_measurement = (
            data["unit"]
        )


        # Liczniki zużycia wody
        if data.get("total"):

            self._attr_device_class = (
                "water"
            )

            self._attr_state_class = (
                "total_increasing"
            )


        # Aktualny przepływ
        if data.get("flow"):

            self._attr_device_class = (
                "volume_flow_rate"
            )

            self._attr_state_class = (
                "measurement"
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
    def native_value(self):

        data = (
            self.coordinator.data[1]
            ["result"]
            ["data"]
            ["json"]
        )


        for item in self.path:

            data = data[item]


        if self.path[-1] == "lastReportedAt":

            return dt_util.parse_datetime(data)


        return data
