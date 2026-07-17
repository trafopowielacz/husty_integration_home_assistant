"""Base entity classes for Husty."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HustyCoordinator


def get_nested_value(
    data: dict[str, Any],
    path: tuple[str, ...],
) -> Any:
    """Return a nested value from a dictionary."""

    value: Any = data

    for key in path:
        if not isinstance(value, dict):
            return None

        value = value.get(key)

        if value is None:
            return None

    return value


class HustyEntity(
    CoordinatorEntity[HustyCoordinator]
):
    """Base representation of a Husty entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HustyCoordinator,
        key: str,
    ) -> None:
        """Initialize a Husty entity."""

        super().__init__(coordinator)

        self._key = key

        device_id = str(
            coordinator.data.get("deviceId", "unknown")
        )

        self._attr_unique_id = (
            f"{device_id}_{key}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return the Home Assistant device information."""

        data = self.coordinator.data
        core = data.get("core", {})
        metadata = data.get("metadata", {})

        device_id = str(
            data.get("deviceId", "unknown")
        )

        model = (
            metadata.get("modelName")
            or "Uzdatniacz wody"
        )

        return DeviceInfo(
            identifiers={
                (DOMAIN, device_id)
            },
            name=f"Husty {model}",
            manufacturer="Husty",
            model=model,
            sw_version=core.get("version"),
            serial_number=device_id,
            configuration_url="https://app.husty.pl",
        )
