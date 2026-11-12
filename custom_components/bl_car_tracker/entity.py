"""Shared base entity for the BL Car Tracker integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import ATTR_ENTITY_PICTURE
from homeassistant.core import Event, EventStateChangedData, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_CONNECTED_PAIRED_DEVICES,
    ATTR_CONNECTED_PERSON,
    CONF_MAC,
    CONF_PERSON,
    CONF_PHONE_SENSOR,
    CONF_PICTURE,
    DOMAIN,
    SUBENTRY_PERSON,
    SUBENTRY_VEHICLE,
)
from .media import image_unique_id, uploaded_filename


def add_vehicle_entities(
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    entity_class: type[BLCarTrackerEntity],
) -> None:
    """Create one entity of `entity_class` per vehicle subentry."""
    for subentry in entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_VEHICLE:
            async_add_entities(
                [entity_class(entry, subentry)],
                config_subentry_id=subentry.subentry_id,
            )


class BLCarTrackerEntity(Entity):
    """Tracks which person's phone is connected to the vehicle's Bluetooth device.

    Every configured person can drive every vehicle. Subclasses override
    `_refresh` to react to the result, then call super.
    """

    _attr_has_entity_name = True
    _attr_name = None  # entity takes the device (vehicle) name
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, subentry: ConfigSubentry) -> None:
        self._mac: str = subentry.data[CONF_MAC]
        self._persons: list[Mapping[str, Any]] = [
            s.data for s in entry.subentries.values() if s.subentry_type == SUBENTRY_PERSON
        ]
        self._connected_person: str | None = None
        self._attr_unique_id = subentry.subentry_id
        picture = subentry.data.get(CONF_PICTURE)
        # An uploaded picture is mirrored from the authenticated image entity.
        self._image_unique_id = (
            image_unique_id(subentry.subentry_id) if uploaded_filename(picture) else None
        )
        self._attr_entity_picture = None if self._image_unique_id else picture
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)}, name=subentry.title
        )

    async def async_added_to_hass(self) -> None:
        """Watch every phone sensor and person, then compute the initial state."""
        await super().async_added_to_hass()
        entity_ids = [p[CONF_PHONE_SENSOR] for p in self._persons]
        entity_ids += [p[CONF_PERSON] for p in self._persons]
        self.async_on_remove(
            async_track_state_change_event(self.hass, entity_ids, self._handle_change)
        )
        self._refresh()
        if self._image_unique_id and (
            image_id := er.async_get(self.hass).async_get_entity_id(
                "image", DOMAIN, self._image_unique_id
            )
        ):
            self._copy_picture(image_id)
            self.async_on_remove(
                async_track_state_change_event(self.hass, [image_id], self._handle_image)
            )

    @callback
    def _copy_picture(self, image_id: str) -> None:
        if state := self.hass.states.get(image_id):
            self._attr_entity_picture = state.attributes.get(ATTR_ENTITY_PICTURE)

    @callback
    def _handle_image(self, event: Event[EventStateChangedData]) -> None:
        # The image proxy token rotates, so the signed URL has to follow.
        self._copy_picture(event.data["entity_id"])
        self.async_write_ha_state()

    @callback
    def _handle_change(self, event: Event[EventStateChangedData]) -> None:
        self._refresh()
        self.async_write_ha_state()

    @callback
    def _refresh(self) -> None:
        """Find the first person whose phone is connected to the vehicle."""
        self._connected_person = None
        for person in self._persons:
            state = self.hass.states.get(person[CONF_PHONE_SENSOR])
            if state is None:
                continue
            devices = state.attributes.get(ATTR_CONNECTED_PAIRED_DEVICES) or []
            if any(self._mac in device.upper() for device in devices):
                self._connected_person = person[CONF_PERSON]
                return

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        return {ATTR_CONNECTED_PERSON: self._connected_person}
