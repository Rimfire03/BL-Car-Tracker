"""Storage of vehicle pictures uploaded through the config flow."""

from __future__ import annotations

import shutil
from pathlib import Path

from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.core import HomeAssistant

from .const import MEDIA_DIR, MEDIA_URL

ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def media_path(hass: HomeAssistant) -> Path:
    """Directory holding uploaded pictures, served at MEDIA_URL."""
    return Path(hass.config.path(MEDIA_DIR))


def save_picture(hass: HomeAssistant, file_id: str, name: str) -> str | None:
    """Copy an uploaded image into the media directory and return its URL.

    Blocking: run in the executor. Returns None if the file is not an image.
    """
    with process_uploaded_file(hass, file_id) as source:
        suffix = source.suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            return None
        target_dir = media_path(hass)
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{name}{suffix}"
        shutil.copyfile(source, target_dir / filename)
    return f"{MEDIA_URL}/{filename}"


def delete_picture(hass: HomeAssistant, url: str | None) -> None:
    """Delete a picture stored by `save_picture` (blocking). Ignores other URLs."""
    if url and url.startswith(f"{MEDIA_URL}/"):
        (media_path(hass) / url.removeprefix(f"{MEDIA_URL}/")).unlink(missing_ok=True)
