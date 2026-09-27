"""Config flow for the Vehicle Presence integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_MAC,
    CONF_PERSON,
    CONF_PERSONS,
    CONF_PHONE_SENSOR,
    CONF_PICTURE,
    DOMAIN,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Required(CONF_MAC): str,
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


class VehiclePresenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vehicle Presence."""

    VERSION = 1

    def __init__(self) -> None:
        self._vehicle_data: dict[str, Any] = {}
        self._persons: list[dict[str, str]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Collect the vehicle's name, MAC address and optional picture."""
        if user_input is not None:
            self._vehicle_data = {
                "name": user_input["name"],
                CONF_MAC: user_input[CONF_MAC].upper(),
                CONF_PICTURE: user_input.get(CONF_PICTURE),
            }
            return await self.async_step_person()

        return self.async_show_form(step_id="user", data_schema=STEP_USER_SCHEMA)

    async def async_step_person(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Collect one phone-sensor / person pair; loop until the user is done.

        The first pair added is used as the fallback owner when no known
        phone is currently paired with the vehicle.
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

            data = {**self._vehicle_data, CONF_PERSONS: self._persons}
            return self.async_create_entry(title=self._vehicle_data["name"], data=data)

        return self.async_show_form(step_id="person", data_schema=STEP_PERSON_SCHEMA)
