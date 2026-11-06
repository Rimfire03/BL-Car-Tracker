"""Device tracker platform for the Vehicle Presence integration."""

from __future__ import annotations

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_GPS_ACCURACY, ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .entity import VehiclePresenceEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the vehicle tracker from a config entry."""
    async_add_entities([VehicleTracker(entry)])


class VehicleTracker(VehiclePresenceEntity, TrackerEntity, RestoreEntity):
    """Vehicle position, copied from the connected person.

    While a known phone is connected to the vehicle, the position follows that
    person. Once disconnected, the last position is kept (the parking spot),
    including across Home Assistant restarts.
    """

    _attr_source_type = SourceType.GPS

    async def async_added_to_hass(self) -> None:
        """Restore the last known position, then start tracking."""
        if (last := await self.async_get_last_state()) is not None:
            self._attr_latitude = last.attributes.get(ATTR_LATITUDE)
            self._attr_longitude = last.attributes.get(ATTR_LONGITUDE)
            self._attr_location_accuracy = last.attributes.get(ATTR_GPS_ACCURACY) or 0
        await super().async_added_to_hass()

    @callback
    def _refresh(self) -> None:
        super()._refresh()
        if self._connected_person is None:
            return
        person = self.hass.states.get(self._connected_person)
        if person is None:
            return
        latitude = person.attributes.get(ATTR_LATITUDE)
        longitude = person.attributes.get(ATTR_LONGITUDE)
        if latitude is None or longitude is None:
            return
        self._attr_latitude = latitude
        self._attr_longitude = longitude
        self._attr_location_accuracy = person.attributes.get(ATTR_GPS_ACCURACY) or 0
