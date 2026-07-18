"""Base entities for Husty."""

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
    """Get nested value."""

    value = data

    for item in path:
        if isinstance(value, list):
            try:
                value = value[int(item)]
            except (ValueError, IndexError):
                return None

        elif isinstance(value, dict):
            value = value.get(item)

        else:
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

        super().__init__(coordinator)

        self._attr_unique_id = (
            f"{coordinator.data.get('deviceId')}_{key}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Main Husty device."""

        data = self.coordinator.data
        core = data.get("core", {})
        metadata = data.get("metadata", {})

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    data.get("deviceId"),
                )
            },
            name=f"Husty {metadata.get('modelName')}",
            manufacturer="Husty",
            model=metadata.get("modelName"),
            sw_version=core.get("version"),
        )


class HustyLeakEntity(CoordinatorEntity[HustyCoordinator]):
    """Leak Protect device entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HustyCoordinator,
        key: str,
    ) -> None:

        super().__init__(coordinator)

        self._attr_unique_id = (
            f"leak_{key}"
        )

    @property
    def leak_data(self) -> dict:
        """Return Leak Protect data."""

        sensors = self.coordinator.data.get(
            "floorSensors",
            [],
        )

        if sensors:
            return sensors[0]

        return {}

    @property
    def device_info(self) -> DeviceInfo:
        """Leak Protect device info."""

        data = self.leak_data

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    data.get("deviceId"),
                )
            },
            name="Husty SaoCal Leak Protect",
            manufacturer="Husty",
            model=data.get(
                "metadata",
                {}
            ).get(
                "modelName"
            ),
            sw_version=data.get(
                "core",
                {}
            ).get(
                "version"
            ),
        )
