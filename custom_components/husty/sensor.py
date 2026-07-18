"""Sensor platform for Husty."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfMass,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)
from homeassistant.util import dt as dt_util

from . import HustyConfigEntry
from .entity import (
    HustyEntity,
    HustyLeakEntity,
    get_nested_value,
)


@dataclass(
    frozen=True,
    kw_only=True,
)
class HustySensorEntityDescription(
    SensorEntityDescription
):
    """Description of Husty sensor."""

    path: tuple[str, ...]
    value_fn: Callable[[Any], Any] | None = None
    leak_sensor: bool = False


def parse_timestamp(
    value: Any,
) -> datetime | None:
    """Convert timestamp."""

    if not isinstance(value, str):
        return None

    return dt_util.parse_datetime(value)


SENSORS = (

    # -------------------------
    # SAOCAL 250 LE
    # -------------------------

    HustySensorEntityDescription(
        key="salt",
        name="Sól",
        icon="mdi:shaker",
        path=(
            "core",
            "saltLevel1",
        ),
        native_unit_of_measurement=(
            UnitOfMass.KILOGRAMS
        ),
        state_class=SensorStateClass.MEASUREMENT,
    ),

    HustySensorEntityDescription(
        key="water_remaining",
        name="Pozostała woda",
        icon="mdi:water",
        path=(
            "core",
            "waterSupply",
        ),
        native_unit_of_measurement=(
            UnitOfVolume.LITERS
        ),
        state_class=SensorStateClass.MEASUREMENT,
    ),

    HustySensorEntityDescription(
        key="water_remaining_percent",
        name="Pozostała woda procent",
        icon="mdi:water-percent",
        path=(
            "core",
            "waterSupplyPercent",
        ),
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    HustySensorEntityDescription(
        key="water_flow",
        name="Przepływ wody",
        icon="mdi:water-pump",
        path=(
            "core",
            "waterFlow",
        ),
        native_unit_of_measurement=(
            UnitOfVolumeFlowRate.LITERS_PER_MINUTE
        ),
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    HustySensorEntityDescription(
        key="water_today",
        name="Zużycie wody dzisiaj",
        icon="mdi:water-check",
        path=(
            "core",
            "consumption",
            "today",
            "total",
        ),
        native_unit_of_measurement=(
            UnitOfVolume.LITERS
        ),
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),

    HustySensorEntityDescription(
        key="water_yesterday",
        name="Zużycie wody wczoraj",
        icon="mdi:water-minus",
        path=(
            "core",
            "consumption",
            "yesterday",
            "total",
        ),
        native_unit_of_measurement=(
            UnitOfVolume.LITERS
        ),
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
    ),

    HustySensorEntityDescription(
        key="water_week",
        name="Zużycie wody tydzień",
        icon="mdi:calendar-week",
        path=(
            "core",
            "consumption",
            "week",
            "total",
        ),
        native_unit_of_measurement=(
            UnitOfVolume.LITERS
        ),
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),

    HustySensorEntityDescription(
        key="water_month",
        name="Zużycie wody miesiąc",
        icon="mdi:calendar-month",
        path=(
            "core",
            "consumption",
            "month",
            "total",
        ),
        native_unit_of_measurement=(
            UnitOfVolume.LITERS
        ),
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),

    HustySensorEntityDescription(
        key="water_year",
        name="Zużycie wody rok",
        icon="mdi:calendar",
        path=(
            "core",
            "consumption",
            "year",
            "total",
        ),
        native_unit_of_measurement=(
            UnitOfVolume.LITERS
        ),
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),

    HustySensorEntityDescription(
        key="days_to_regeneration",
        name="Dni do regeneracji",
        icon="mdi:calendar-refresh",
        path=(
            "core",
            "remainingDaysToNextRegeneration",
        ),
        native_unit_of_measurement="dni",
    ),

    HustySensorEntityDescription(
        key="salt_regenerations",
        name="Pozostałe regeneracje z soli",
        icon="mdi:counter",
        path=(
            "core",
            "saltRegenerationsLeft",
        ),
    ),

    HustySensorEntityDescription(
        key="last_update",
        name="Ostatnie połączenie",
        icon="mdi:cloud-clock",
        path=(
            "metadata",
            "lastUpdatedAt",
        ),
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=parse_timestamp,
    ),


    # -------------------------
    # LEAK PROTECT
    # -------------------------

    HustySensorEntityDescription(
        key="leak_temperature",
        name="Temperatura",
        icon="mdi:thermometer",
        path=(
            "core",
            "temperature",
        ),
        native_unit_of_measurement=(
            UnitOfTemperature.CELSIUS
        ),
        leak_sensor=True,
    ),

    HustySensorEntityDescription(
        key="leak_humidity",
        name="Wilgotność",
        icon="mdi:water-percent",
        path=(
            "core",
            "humidity",
        ),
        native_unit_of_measurement=PERCENTAGE,
        leak_sensor=True,
    ),

    HustySensorEntityDescription(
        key="leak_battery",
        name="Bateria",
        icon="mdi:battery",
        path=(
            "core",
            "battery",
        ),
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        leak_sensor=True,
    ),

    HustySensorEntityDescription(
        key="leak_last_update",
        name="Ostatnia aktualizacja",
        icon="mdi:clock",
        path=(
            "metadata",
            "lastUpdatedAt",
        ),
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=parse_timestamp,
        leak_sensor=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HustyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create Husty sensors."""

    coordinator = entry.runtime_data

    entities = []

    for description in SENSORS:

        if description.leak_sensor:
            entities.append(
                HustyLeakSensor(
                    coordinator,
                    description,
                )
            )

        else:
            entities.append(
                HustySensor(
                    coordinator,
                    description,
                )
            )

    async_add_entities(entities)


class HustySensor(
    HustyEntity,
    SensorEntity,
):
    """Main Husty sensor."""

    def __init__(
        self,
        coordinator,
        description,
    ) -> None:

        super().__init__(
            coordinator,
            description.key,
        )

        self.entity_description = description


    @property
    def native_value(self):

        value = get_nested_value(
            self.coordinator.data,
            self.entity_description.path,
        )

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(
                value
            )

        return value



class HustyLeakSensor(
    HustyLeakEntity,
    SensorEntity,
):
    """Leak Protect sensor."""

    def __init__(
        self,
        coordinator,
        description,
    ) -> None:

        super().__init__(
            coordinator,
            description.key,
        )

        self.entity_description = description


    @property
    def native_value(self):

        value = get_nested_value(
            self.leak_data,
            self.entity_description.path,
        )

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(
                value
            )

        return value
