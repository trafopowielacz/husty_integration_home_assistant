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
from .entity import HustyEntity, get_nested_value


@dataclass(
    frozen=True,
    kw_only=True,
)
class HustyBinarySensorEntityDescription(
    BinarySensorEntityDescription
):
    """Describe a Husty binary sensor."""

    path: tuple[str, ...]
    value_fn: Callable[[Any], bool] = bool


BINARY_SENSOR_DESCRIPTIONS: tuple[
    HustyBinarySensorEntityDescription,
    ...,
] = (
    HustyBinarySensorEntityDescription(
        key="online",
        name="Połączenie",
        icon="mdi:cloud-check",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        path=(
            "metadata",
            "isConnected",
        ),
        value_fn=bool,
    ),
    HustyBinarySensorEntityDescription(
        key="regeneration_active",
        name="Regeneracja",
        icon="mdi:autorenew",
        device_class=BinarySensorDeviceClass.RUNNING,
        path=(
            "core",
            "regenerationInProgress",
        ),
        value_fn=bool,
    ),
    HustyBinarySensorEntityDescription(
        key="leak_protection",
        name="Ochrona przed wyciekiem",
        icon="mdi:water-lock",
        path=(
            "core",
            "leakageProtectionState",
        ),
        value_fn=lambda value: value == "automatic",
    ),
    HustyBinarySensorEntityDescription(
        key="firmware_update_available",
        name="Dostępna aktualizacja",
        icon="mdi:update",
        device_class=BinarySensorDeviceClass.UPDATE,
        path=(
            "core",
            "newFirmwareAvailable",
        ),
        value_fn=bool,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HustyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Husty binary sensors."""

    coordinator = entry.runtime_data

    async_add_entities(
        HustyBinarySensor(
            coordinator,
            description,
        )
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class HustyBinarySensor(
    HustyEntity,
    BinarySensorEntity,
):
    """Representation of a Husty binary sensor."""

    entity_description: (
        HustyBinarySensorEntityDescription
    )

    def __init__(
        self,
        coordinator,
        description: (
            HustyBinarySensorEntityDescription
        ),
    ) -> None:
        """Initialize the binary sensor."""

        super().__init__(
            coordinator,
            description.key,
        )

        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""

        value = get_nested_value(
            self.coordinator.data,
            self.entity_description.path,
        )

        if value is None:
            return None

        return self.entity_description.value_fn(
            value
        )
