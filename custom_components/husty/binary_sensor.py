"""Binary sensor platform for Husty."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
)

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
class HustyBinarySensorDescription(
    BinarySensorEntityDescription
):
    """Describe Husty binary sensor."""

    path: tuple[str, ...]
    value_fn: Callable[[Any], bool]
    leak_sensor: bool = False


BINARY_SENSORS = (

    # =========================
    # SAOCAL 250 LE
    # =========================

    HustyBinarySensorDescription(
        key="connection",
        name="Połączenie",
        icon="mdi:cloud-check",
        device_class=(
            BinarySensorDeviceClass.CONNECTIVITY
        ),
        path=(
            "metadata",
            "isConnected",
        ),
        value_fn=bool,
    ),

    HustyBinarySensorDescription(
        key="regeneration",
        name="Regeneracja",
        icon="mdi:autorenew",
        device_class=(
            BinarySensorDeviceClass.RUNNING
        ),
        path=(
            "core",
            "regenerationInProgress",
        ),
        value_fn=bool,
    ),

    HustyBinarySensorDescription(
        key="leak_protection",
        name="Ochrona przed wyciekiem",
        icon="mdi:water-lock",
        path=(
            "core",
            "leakageProtectionState",
        ),
        value_fn=lambda value: (
            value == "automatic"
        ),
    ),


    # =========================
    # LEAK PROTECT
    # =========================

    HustyBinarySensorDescription(
        key="flood_detected",
        name="Wykrycie zalania",
        icon="mdi:water-alert",
        device_class=(
            BinarySensorDeviceClass.MOISTURE
        ),
        path=(
            "core",
            "floodDetected",
        ),
        value_fn=bool,
        leak_sensor=True,
    ),

    HustyBinarySensorDescription(
        key="leak_connection",
        name="Połączenie Leak Protect",
        icon="mdi:cloud-check",
        device_class=(
            BinarySensorDeviceClass.CONNECTIVITY
        ),
        path=(
            "metadata",
            "isConnected",
        ),
        value_fn=bool,
        leak_sensor=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HustyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create Husty binary sensors."""

    coordinator = entry.runtime_data

    entities = []

    for description in BINARY_SENSORS:

        if description.leak_sensor:
            entities.append(
                HustyLeakBinarySensor(
                    coordinator,
                    description,
                )
            )

        else:
            entities.append(
                HustyBinarySensor(
                    coordinator,
                    description,
                )
            )

    async_add_entities(entities)


class HustyBinarySensor(
    HustyEntity,
    BinarySensorEntity,
):
    """Main Husty binary sensor."""

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
    def is_on(self):

        value = get_nested_value(
            self.coordinator.data,
            self.entity_description.path,
        )

        return self.entity_description.value_fn(
            value
        )



class HustyLeakBinarySensor(
    HustyLeakEntity,
    BinarySensorEntity,
):
    """Leak Protect binary sensor."""

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
    def is_on(self):

        value = get_nested_value(
            self.leak_data,
            self.entity_description.path,
        )

        return self.entity_description.value_fn(
            value
        )
