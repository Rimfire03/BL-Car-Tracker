"""Binary sensor platform for the Vehicle Presence integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import VehiclePresenceEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the vehicle occupancy sensor from a config entry."""
    async_add_entities([VehicleOccupancySensor(entry)])


class VehicleOccupancySensor(VehiclePresenceEntity, BinarySensorEntity):
    """On while a known person's phone is connected to the vehicle."""

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    @property
    def is_on(self) -> bool:
        return self._connected_person is not None
