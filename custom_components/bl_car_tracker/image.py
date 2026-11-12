"""Image platform: uploaded vehicle pictures, served behind authentication."""

from __future__ import annotations

import mimetypes

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_PICTURE, DOMAIN, SUBENTRY_VEHICLE
from .media import image_unique_id, media_path, uploaded_filename


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up one image entity per vehicle that has an uploaded picture."""
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_VEHICLE:
            continue
        if filename := uploaded_filename(subentry.data.get(CONF_PICTURE)):
            async_add_entities(
                [VehicleImage(hass, subentry, filename)],
                config_subentry_id=subentry.subentry_id,
            )


class VehicleImage(ImageEntity):
    """Picture of a vehicle. Home Assistant's image proxy signs its URL."""

    _attr_has_entity_name = True
    _attr_name = None  # entity takes the device (vehicle) name
    _attr_should_poll = False

    def __init__(
        self, hass: HomeAssistant, subentry: ConfigSubentry, filename: str
    ) -> None:
        super().__init__(hass)
        self._path = media_path(hass) / filename
        self._attr_unique_id = image_unique_id(subentry.subentry_id)
        self._attr_content_type = mimetypes.guess_type(filename)[0] or "image/jpeg"
        self._attr_image_last_updated = dt_util.utcnow()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)}
        )

    async def async_image(self) -> bytes | None:
        return await self.hass.async_add_executor_job(self._read)

    def _read(self) -> bytes | None:
        try:
            return self._path.read_bytes()
        except OSError:
            return None
