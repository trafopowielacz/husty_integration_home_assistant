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
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)
from homeassistant.util import dt as dt_util

from . import HustyConfigEntry
from .entity import HustyEntity, get_nested_value


@dataclass(
    frozen=True,
    kw_only=True,
)
class HustySensorEntityDescription(
    SensorEntityDescription
):
    """Describe a Husty sensor."""

    path: tuple[str, ...]
    value_fn: Callable[[Any], Any] | None = None


def parse_timestamp(value: Any) -> datetime | None:
    """Parse an ISO timestamp returned by Husty."""

    if not isinstance(value, str):
        return None

    parsed = dt_util.parse_datetime(value)

    if parsed is None:
        return None

    return parsed


SENSOR_DESCRIPTIONS: tuple[
    HustySensorEntityDescription,
    ...,
] = (
    HustySensorEntityDescription(
        key="salt_level",
        name="Sól",
        icon="mdi:shaker",
        path=("core", "saltLevel1"),
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HustySensorEntityDescription(
        key="salt_capacity",
        name="Pojemność zbiornika soli",
        icon="mdi:shaker-outline",
        path=("core", "saltCapacity"),
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        entity_registry_enabled_default=False,
    ),
    HustySensorEntityDescription(
        key="water_remaining",
        name="Pozostała woda",
        icon="mdi:water",
        path=("core", "waterSupply"),
        native_unit_of_measurement=UnitOfVolume.LITERS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HustySensorEntityDescription(
        key="water_remaining_percent",
        name="Pozostała woda",
        translation_key="water_remaining_percent",
        icon="mdi:water-percent",
        path=("core", "waterSupplyPercent"),
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HustySensorEntityDescription(
        key="water_flow",
        name="Przepływ wody",
        icon="mdi:water-pump",
        path=("core", "waterFlow"),
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=(
            UnitOfVolumeFlowRate.LITERS_PER_MINUTE
        ),
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HustySensorEntityDescription(
        key="water_consumption_today",
        name="Zużycie wody dzisiaj",
        icon="mdi:water-check",
        path=(
            "core",
            "consumption",
            "today",
            "total",
        ),
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    HustySensorEntityDescription(
        key="water_consumption_yesterday",
        name="Zużycie wody wczoraj",
        icon="mdi:water-minus",
        path=(
            "core",
            "consumption",
            "yesterday",
            "total",
        ),
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=False,
    ),
    HustySensorEntityDescription(
        key="water_consumption_week",
        name="Zużycie wody w tym tygodniu",
        icon="mdi:calendar-week",
        path=(
            "core",
            "consumption",
            "week",
            "total",
        ),
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    HustySensorEntityDescription(
        key="water_consumption_month",
        name="Zużycie wody w tym miesiącu",
        icon="mdi:calendar-month",
        path=(
            "core",
            "consumption",
            "month",
            "total",
        ),
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    HustySensorEntityDescription(
        key="water_consumption_year",
        name="Zużycie wody w tym roku",
        icon="mdi:calendar",
        path=(
            "core",
            "consumption",
            "year",
            "total",
        ),
        device_class=SensorDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.LITERS,
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
        native_unit_of_measurement="d",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HustySensorEntityDescription(
        key="salt_regenerations_left",
        name="Pozostałe regeneracje z soli",
        icon="mdi:counter",
        path=("core", "saltRegenerationsLeft"),
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HustySensorEntityDescription(
        key="regeneration_time",
        name="Planowana godzina regeneracji",
        icon="mdi:clock-outline",
        path=("core", "delayedRegenerationTime"),
    ),
    HustySensorEntityDescription(
        key="last_reported",
        name="Ostatnie połączenie",
        icon="mdi:cloud-clock",
        path=("metadata", "lastReportedAt"),
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=parse_timestamp,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HustyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Husty sensors."""

    coordinator = entry.runtime_data

    async_add_entities(
        HustySensor(
            coordinator,
            description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class HustySensor(
    HustyEntity,
    SensorEntity,
):
    """Representation of a Husty sensor."""

    entity_description: HustySensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: HustySensorEntityDescription,
    ) -> None:
        """Initialize the Husty sensor."""

        super().__init__(
            coordinator,
            description.key,
        )

        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""

        value = get_nested_value(
            self.device_data,
            self.entity_description.path,
        )

        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(value)

        return value
