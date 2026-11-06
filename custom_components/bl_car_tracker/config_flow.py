"""Config flow for the BL Car Tracker integration."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    CONF_MAC,
    CONF_PERSON,
    CONF_PERSONS,
    CONF_PHONE_SENSOR,
    CONF_PICTURE,
    CONF_PICTURE_FILE,
    DOMAIN,
)
from .media import save_picture

MAC_PATTERN = re.compile(r"^([0-9A-F]{2}[:-]){5}[0-9A-F]{2}$")

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_MAC): str,
        vol.Optional(CONF_PICTURE_FILE): selector.FileSelector(
            selector.FileSelectorConfig(accept="image/*")
        ),
        vol.Optional(CONF_PICTURE): str,
    }
)

STEP_PERSON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PHONE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_PERSON): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="person")
        ),
        vol.Required("add_another", default=False): bool,
    }
)


class BLCarTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BL Car Tracker."""

    VERSION = 1

    def __init__(self) -> None:
        self._vehicle_data: dict[str, Any] = {}
        self._persons: list[dict[str, str]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Collect the vehicle's name, Bluetooth MAC address and optional picture."""
        errors: dict[str, str] = {}
        if user_input is not None:
            mac = user_input[CONF_MAC].strip().upper()
            if not MAC_PATTERN.match(mac):
                errors[CONF_MAC] = "invalid_mac"
            else:
                mac = mac.replace("-", ":")
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()
                picture = user_input.get(CONF_PICTURE)
                if file_id := user_input.get(CONF_PICTURE_FILE):
                    picture = await self.hass.async_add_executor_job(
                        save_picture, self.hass, file_id, mac.replace(":", "").lower()
                    )
                    if picture is None:
                        errors[CONF_PICTURE_FILE] = "invalid_image"
                if not errors:
                    self._vehicle_data = {
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_MAC: mac,
                        CONF_PICTURE: picture,
                    }
                    return await self.async_step_person()

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_SCHEMA, user_input
            ),
            errors=errors,
        )

    async def async_step_person(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Collect one phone-sensor / person pair; loop until the user is done.

        When several phones are connected at once, the first pair added wins.
        """
        if user_input is not None:
            self._persons.append(
                {
                    CONF_PHONE_SENSOR: user_input[CONF_PHONE_SENSOR],
                    CONF_PERSON: user_input[CONF_PERSON],
                }
            )
            if user_input["add_another"]:
                return await self.async_step_person()

            return self.async_create_entry(
                title=self._vehicle_data[CONF_NAME],
                data={**self._vehicle_data, CONF_PERSONS: self._persons},
            )

        return self.async_show_form(step_id="person", data_schema=STEP_PERSON_SCHEMA)
