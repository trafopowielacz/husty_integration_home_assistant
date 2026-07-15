from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


SENSORS = {

    "Sól":
        (
            ["core","saltLevel1"],
            "kg"
        ),


    "Pozostała woda":
        (
            ["core","waterSupply"],
            "L"
        ),


    "Pozostała woda procent":
        (
            ["core","waterSupplyPercent"],
            "%"
        ),


    "Przepływ":
        (
            ["core","waterFlow"],
            "L/min"
        ),


    "Zużycie dzisiaj":
        (
            [
                "core",
                "consumption",
                "today",
                "total"
            ],
            "L"
        ),


    "Zużycie miesiąc":
        (
            [
                "core",
                "consumption",
                "month",
                "total"
            ],
            "L"
        ),


    "Dni do regeneracji":
        (
            [
                "core",
                "remainingDaysToNextRegeneration"
            ],
            "dni"
        ),
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
                name,
                path,
                unit
            )

            for name,(path,unit)
            in SENSORS.items()
        ]
    )



class HustySensor(
    SensorEntity
):

    def __init__(
        self,
        coordinator,
        name,
        path,
        unit
    ):

        self.coordinator = coordinator

        self._attr_name = (
            "Husty " + name
        )

        self.path = path

        self._attr_native_unit_of_measurement = unit



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


        return data