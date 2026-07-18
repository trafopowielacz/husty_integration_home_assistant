"""Base entities for Husty."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HustyCoordinator


def get_nested_value(
    data: dict[str, Any] | list | None,
    path: tuple[str, ...],
) -> Any:
    """Get nested value from dict/list."""

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
    """Base entity for main Husty device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HustyCoordinator,
        key: str,
    ) -> None:
        """Initialize main device entity."""

        super().__init__(coordinator)

        device_id = coordinator.data.get(
            "deviceId",
            "unknown",
        )

        self._attr_unique_id = (
            f"{device_id}_{key}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return main device info."""

        data = self.coordinator.data

        core = data.get(
            "core",
            {},
        )

        metadata = data.get(
            "metadata",
            {},
        )

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    data.get("deviceId"),
                )
            },
            name=f"Husty {metadata.get('modelName', 'SaoCal')}",
            manufacturer="Husty",
            model=metadata.get(
                "modelName",
                "SaoCal 250 LE",
            ),
            sw_version=core.get(
                "version",
            ),
        )


class HustyLeakEntity(CoordinatorEntity[HustyCoordinator]):
    """Base entity for Leak Protect module."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HustyCoordinator,
        key: str,
    ) -> None:
        """Initialize Leak Protect entity."""

        super().__init__(coordinator)

        sensors = coordinator.data.get(
            "floorSensors",
            [],
        )

        device_id = "unknown"

        if sensors:
            device_id = sensors[0].get(
                "deviceId",
                "unknown",
            )

        self._attr_unique_id = (
            f"{device_id}_{key}"
        )

    @property
    def leak_data(self) -> dict[str, Any]:
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
        """Return Leak Protect device info."""

        data = self.leak_data

        core = data.get(
            "core",
            {},
        )

        metadata = data.get(
            "metadata",
            {},
        )

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    data.get("deviceId"),
                )
            },
            name="Husty SaoCal Leak Protect",
            manufacturer="Husty",
            model=metadata.get(
                "modelName",
                "Leak Protect",
            ),
            sw_version=core.get(
                "version",
            ),
        )
