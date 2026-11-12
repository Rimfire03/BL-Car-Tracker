"""Storage of vehicle pictures uploaded through the config flow.

Files are never served directly: the image platform exposes them through an
authenticated `image` entity.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.core import HomeAssistant

from .const import MEDIA_DIR, MEDIA_URL

ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def media_path(hass: HomeAssistant) -> Path:
    """Directory holding uploaded pictures."""
    return Path(hass.config.path(MEDIA_DIR))


def uploaded_filename(picture: str | None) -> str | None:
    """File name of an uploaded picture, or None for a plain URL or no picture."""
    if picture and picture.startswith(f"{MEDIA_URL}/"):
        return Path(picture).name
    return None


def image_unique_id(subentry_id: str) -> str:
    """Unique id of the image entity of a vehicle."""
    return f"{subentry_id}_image"


def save_picture(hass: HomeAssistant, file_id: str, name: str) -> str | None:
    """Copy an uploaded image into the media directory and return its stored reference.

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


def prune_pictures(hass: HomeAssistant, keep: set[str | None]) -> None:
    """Delete stored pictures whose URL is not in `keep` (blocking)."""
    directory = media_path(hass)
    if not directory.is_dir():
        return
    for file in directory.iterdir():
        if f"{MEDIA_URL}/{file.name}" not in keep:
            file.unlink(missing_ok=True)
