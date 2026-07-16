from datetime import datetime

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import DOMAIN


SENSORS = {

    "salt": {
        "name": "Sól",
        "icon": "mdi:shaker-outline",
        "unit": "kg",
    },

    "water_left": {
        "name": "Pozostała woda",
        "icon": "mdi:water",
        "unit": "L",
    },

    "water_left_percent": {
        "name": "Pozostała woda procent",
        "icon": "mdi:water-percent",
        "unit": "%",
    },

    "flow": {
        "name": "Przepływ wody",
        "icon": "mdi:water-pump",
        "unit": "L/min",
    },

    "water_today": {
        "name": "Zużycie wody dzisiaj",
        "icon": "mdi:water",
        "unit": "L",
    },

    "water_month": {
        "name": "Zużycie wody miesiąc",
        "icon": "mdi:calendar-month",
        "unit": "L",
    },

    "water_hour": {
        "name": "Zużycie wody aktualna godzina",
        "icon": "mdi:clock-water",
        "unit": "L",
    },

    "regeneration_left": {
        "name": "Regeneracja za",
        "icon": "mdi:autorenew",
        "unit": "dni",
    },

    "salt_regenerations": {
        "name": "Pozostałe regeneracje z soli",
        "icon": "mdi:counter",
        "unit": None,
    },

}


async def async_setup_entry(hass, entry, async_add_entities):

    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for key, cfg in SENSORS.items():

        entities.append(
            HustySensor(
                coordinator,
                key,
                cfg,
            )
        )

    async_add_entities(entities)


class HustySensor(CoordinatorEntity, SensorEntity):

    def __init__(
        self,
        coordinator,
        key,
        cfg,
    ):

        super().__init__(coordinator)

        self.key = key
        self.cfg = cfg

        self._attr_name = (
            f"Husty {cfg['name']}"
        )

        self._attr_icon = cfg["icon"]

        if cfg["unit"]:
            self._attr_native_unit_of_measurement = (
                cfg["unit"]
            )


    @property
    def unique_id(self):

        return (
            f"husty_{self.key}"
        )


    @property
    def native_value(self):

        data = (
            self.coordinator.data[1]
            ["result"]
            ["data"]
            ["json"]
        )

        core = data.get(
            "core",
            {}
        )


        if self.key == "salt":

            return core.get(
                "saltLevel1"
            )


        if self.key == "water_left":

            return core.get(
                "waterSupply"
            )


        if self.key == "water_left_percent":

            return core.get(
                "waterSupplyPercent"
            )


        if self.key == "flow":

            return core.get(
                "waterFlow"
            )


        if self.key == "water_today":

            return (
                core
                .get("consumption", {})
                .get("today", {})
                .get("total")
            )


        if self.key == "water_month":

            return (
                core
                .get("consumption", {})
                .get("month", {})
                .get("total")
            )


        if self.key == "water_hour":

            hour = datetime.now().hour

            values = (
                core
                .get("consumption", {})
                .get("today", {})
                .get("value", [])
            )

            if len(values) > hour:
                return values[hour]

            return 0


        if self.key == "regeneration_left":

            return core.get(
                "remainingDaysToNextRegeneration"
            )


        if self.key == "salt_regenerations":

            return core.get(
                "saltRegenerationsLeft"
            )


        return None


    @property
    def extra_state_attributes(self):

        if self.key == "water_today":

            data = (
                self.coordinator.data[1]
                ["result"]
                ["data"]
                ["json"]
            )

            values = (
                data["core"]
                ["consumption"]
                ["today"]
                ["value"]
            )

            return {
                f"{h:02}:00": value
                for h, value in enumerate(values)
            }


        return {}
