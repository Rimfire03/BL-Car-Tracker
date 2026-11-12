"""The BL Car Tracker integration."""

from __future__ import annotations

from collections.abc import Iterator

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_PICTURE, DOMAIN, SUBENTRY_VEHICLE
from .media import media_path, prune_pictures
from .migration import async_migrate_legacy_entries

# Images first: the other entities mirror the signed picture URL of their image.
IMAGE_PLATFORMS = [Platform.IMAGE]
PLATFORMS = [Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


def _pictures(entry: ConfigEntry) -> Iterator[str | None]:
    """Picture URLs of the vehicles of an entry."""
    for subentry in entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_VEHICLE:
            yield subentry.data.get(CONF_PICTURE)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Create the picture directory and migrate version 1 entries."""
    directory = media_path(hass)
    await hass.async_add_executor_job(
        lambda: directory.mkdir(parents=True, exist_ok=True)
    )
    await async_migrate_legacy_entries(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BL Car Tracker: a tracker, a sensor and an image per vehicle."""
    await hass.async_add_executor_job(prune_pictures, hass, set(_pictures(entry)))
    # Adding, editing or removing a person or vehicle reloads the entry.
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, IMAGE_PLATFORMS)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload BL Car Tracker."""
    return await hass.config_entries.async_unload_platforms(
        entry, IMAGE_PLATFORMS + PLATFORMS
    )


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Delete the removed entry's pictures, keeping those other entries use."""
    used = {
        picture
        for other in hass.config_entries.async_entries(DOMAIN)
        if other.entry_id != entry.entry_id
        for picture in _pictures(other)
    }
    await hass.async_add_executor_job(prune_pictures, hass, used)
