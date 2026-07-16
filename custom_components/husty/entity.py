"""Base entity for Husty."""

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
    """Return a nested value or None when the path is missing."""

    value: Any = data

    for item in path:
        if not isinstance(value, dict):
            return None

        value = value.get(item)

        if value is None:
            return None

    return value


class HustyEntity(CoordinatorEntity[HustyCoordinator]):
    """Base Husty entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HustyCoordinator,
        key: str,
    ) -> None:
        """Initialize the entity."""

        super().__init__(coordinator)

        self._key = key
        self._attr_unique_id = (
            f"{coordinator.api.device_id}_{key}"
        )

    @property
    def device_data(self) -> dict[str, Any]:
        """Return normalized device data."""

        return self.coordinator.data.get("device", {})

    @property
    def device_info(self) -> DeviceInfo:
        """Return Home Assistant device information."""

        device = self.device_data
        core = device.get("core", {})
        metadata = device.get("metadata", {})

        device_id = str(
            device.get("deviceId")
            or self.coordinator.api.device_id
        )

        model = (
            core.get("model")
            or metadata.get("modelName")
            or "Uzdatniacz wody"
        )

        return DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"Husty {model}",
            manufacturer="Husty",
            model=model,
            sw_version=core.get("version"),
            serial_number=device_id,
        )
