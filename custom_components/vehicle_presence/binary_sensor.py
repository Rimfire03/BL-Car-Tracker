"""Binary sensor platform for the Vehicle Presence integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_CONNEXION,
    CONF_MAC,
    CONF_PERSON,
    CONF_PERSONS,
    CONF_PHONE_SENSOR,
    CONF_PICTURE,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vehicle Presence binary sensor from a config entry."""
    async_add_entities([VehiclePresenceBinarySensor(entry)])


class VehiclePresenceBinarySensor(BinarySensorEntity):
    """Reports which known person's phone is currently paired with a vehicle.

    Detection works by checking each configured phone's Bluetooth
    "connected_paired_devices" attribute for the vehicle's MAC address.
    When no phone is currently paired, the first configured person is used
    as the fallback location source.
    """

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry) -> None:
        self._mac = entry.data[CONF_MAC]
        self._persons: list[dict[str, str]] = entry.data[CONF_PERSONS]
        self._picture = entry.data.get(CONF_PICTURE)
        self._attr_name = entry.data["name"]
        self._attr_unique_id = entry.entry_id
        self._connexion: str | None = None

    async def async_added_to_hass(self) -> None:
        """Start tracking the configured phone sensors."""
        sensors = [person[CONF_PHONE_SENSOR] for person in self._persons]
        self.async_on_remove(
            async_track_state_change_event(self.hass, sensors, self._handle_source_update)
        )
        self._update_connexion()

    @callback
    def _handle_source_update(self, event: Event[EventStateChangedData]) -> None:
        self._update_connexion()
        self.async_write_ha_state()

    def _update_connexion(self) -> None:
        """Recompute which person's phone (if any) is paired with the vehicle."""
        self._connexion = None
        for person in self._persons:
            state = self.hass.states.get(person[CONF_PHONE_SENSOR])
            if state is None:
                continue
            devices = state.attributes.get("connected_paired_devices") or []
            if any(self._mac in device for device in devices):
                self._connexion = person[CONF_PERSON]
                break

    @property
    def is_on(self) -> bool:
        return self._connexion is not None

    @property
    def extra_state_attributes(self) -> dict:
        attrs: dict = {ATTR_CONNEXION: self._connexion}

        fallback_person = self._persons[0][CONF_PERSON] if self._persons else None
        person_entity_id = self._connexion or fallback_person
        if person_entity_id:
            person_state = self.hass.states.get(person_entity_id)
            if person_state is not None:
                attrs["latitude"] = person_state.attributes.get("latitude")
                attrs["longitude"] = person_state.attributes.get("longitude")
                attrs["gps_accuracy"] = person_state.attributes.get("gps_accuracy")

        if self._picture:
            attrs["entity_picture"] = self._picture

        return attrs
