"""The BL Car Tracker integration."""

from __future__ import annotations

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_PICTURE, DOMAIN, MEDIA_URL
from .media import delete_picture, media_path

PLATFORMS = [Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve uploaded vehicle pictures."""
    directory = media_path(hass)
    await hass.async_add_executor_job(
        lambda: directory.mkdir(parents=True, exist_ok=True)
    )
    await hass.http.async_register_static_paths(
        [StaticPathConfig(MEDIA_URL, str(directory), cache_headers=False)]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a BL Car Tracker config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a BL Car Tracker config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Delete the uploaded picture when the vehicle is removed."""
    await hass.async_add_executor_job(
        delete_picture, hass, entry.data.get(CONF_PICTURE)
    )
