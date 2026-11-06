"""Binary sensor platform for the BL Car Tracker integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import BLCarTrackerEntity, add_vehicle_entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up one occupancy sensor per vehicle."""
    add_vehicle_entities(entry, async_add_entities, VehicleOccupancySensor)


class VehicleOccupancySensor(BLCarTrackerEntity, BinarySensorEntity):
    """On while a known person's phone is connected to the vehicle."""

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    @property
    def is_on(self) -> bool:
        return self._connected_person is not None
