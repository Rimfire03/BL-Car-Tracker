"""Merge v0.2.0 entries (one entry per vehicle) into the single-entry layout.

Runs from `async_setup`, before any entry is set up. The first old entry
becomes the hub; every old entry becomes a vehicle subentry, and the persons
of all entries are merged into person subentries. Each vehicle subentry reuses
its old entry id, so unique ids, entity ids and history are preserved.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.typing import UNDEFINED

from .const import (
    CONF_MAC,
    CONF_PERSON,
    CONF_PHONE_SENSOR,
    CONF_PICTURE,
    DOMAIN,
    SUBENTRY_PERSON,
    SUBENTRY_VEHICLE,
)

LEGACY_PERSONS = "persons"


def _add_subentry(
    hass: HomeAssistant,
    hub: ConfigEntry,
    subentry_type: str,
    title: str,
    data: dict[str, Any],
    unique_id: str,
    subentry_id: str | None = None,
) -> None:
    fields: dict[str, Any] = {"subentry_id": subentry_id} if subentry_id else {}
    hass.config_entries.async_add_subentry(
        hub,
        ConfigSubentry(
            data=MappingProxyType(data),
            subentry_type=subentry_type,
            title=title,
            unique_id=unique_id,
            **fields,
        ),
    )


async def async_migrate_legacy_entries(hass: HomeAssistant) -> None:
    """Convert every version 1 entry; safe to run again if interrupted."""
    legacy = [e for e in hass.config_entries.async_entries(DOMAIN) if e.version < 2]
    if not legacy:
        return
    hub = legacy[0]
    present = {s.unique_id for s in hub.subentries.values()}

    # First occurrence wins, so the first old entry's person order is kept.
    persons: dict[str, str] = {}
    for entry in legacy:
        for person in entry.data.get(LEGACY_PERSONS, []):
            persons.setdefault(person[CONF_PERSON], person[CONF_PHONE_SENSOR])
    for person_id, phone_sensor in persons.items():
        if person_id in present:
            continue
        state = hass.states.get(person_id)
        title = state.name if state else person_id.split(".", 1)[1]
        _add_subentry(
            hass,
            hub,
            SUBENTRY_PERSON,
            title,
            {CONF_PERSON: person_id, CONF_PHONE_SENSOR: phone_sensor},
            unique_id=person_id,
        )

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    for entry in legacy:
        subentry_id = entry.entry_id
        mac = entry.data[CONF_MAC]
        if mac not in present:
            _add_subentry(
                hass,
                hub,
                SUBENTRY_VEHICLE,
                entry.data[CONF_NAME],
                {
                    CONF_NAME: entry.data[CONF_NAME],
                    CONF_MAC: mac,
                    CONF_PICTURE: entry.data.get(CONF_PICTURE),
                },
                unique_id=mac,
                subentry_id=subentry_id,
            )
        for entity in er.async_entries_for_config_entry(entity_registry, entry.entry_id):
            entity_registry.async_update_entity(
                entity.entity_id,
                config_entry_id=hub.entry_id,
                config_subentry_id=subentry_id,
            )
        for device in dr.async_entries_for_config_entry(device_registry, entry.entry_id):
            device_registry.async_update_device(
                device.id,
                add_config_entry_id=hub.entry_id,
                add_config_subentry_id=subentry_id,
                remove_config_entry_id=UNDEFINED if entry is hub else entry.entry_id,
            )

    hass.config_entries.async_update_entry(
        hub, data={}, title="BL Car Tracker", version=2
    )
    for entry in legacy[1:]:
        await hass.config_entries.async_remove(entry.entry_id)
