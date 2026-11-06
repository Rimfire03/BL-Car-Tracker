"""Config flow for the BL Car Tracker integration.

One config entry holds the whole setup. Vehicles and persons are subentries,
added and edited independently from the integration page.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentry,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_MAC,
    CONF_PERSON,
    CONF_PHONE_SENSOR,
    CONF_PICTURE,
    CONF_PICTURE_FILE,
    DOMAIN,
    SUBENTRY_PERSON,
    SUBENTRY_VEHICLE,
)
from .media import save_picture

MAC_PATTERN = re.compile(r"^([0-9A-F]{2}[:-]){5}[0-9A-F]{2}$")

VEHICLE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_MAC): str,
        vol.Optional(CONF_PICTURE_FILE): selector.FileSelector(
            selector.FileSelectorConfig(accept="image/*")
        ),
        vol.Optional(CONF_PICTURE): str,
    }
)

PERSON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PERSON): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="person")
        ),
        vol.Required(CONF_PHONE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
    }
)


class BLCarTrackerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create the single BL Car Tracker entry."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Create the entry; vehicles and persons are added as subentries."""
        return self.async_create_entry(title="BL Car Tracker", data={})

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        return {
            SUBENTRY_VEHICLE: VehicleSubentryFlow,
            SUBENTRY_PERSON: PersonSubentryFlow,
        }


class _SubentryFlow(ConfigSubentryFlow):
    """Shared create / reconfigure plumbing."""

    def _others(self, subentry: ConfigSubentry | None) -> list[Mapping[str, Any]]:
        """Data of the other subentries of the same type."""
        return [
            s.data
            for s in self._get_entry().subentries.values()
            if s.subentry_type == self.handler[1]
            and (subentry is None or s.subentry_id != subentry.subentry_id)
        ]

    def _finish(
        self, subentry: ConfigSubentry | None, title: str, data: dict[str, Any]
    ) -> SubentryFlowResult:
        if subentry is None:
            return self.async_create_entry(title=title, data=data)
        return self.async_update_and_abort(
            self._get_entry(), subentry, title=title, data=data
        )


class VehicleSubentryFlow(_SubentryFlow):
    """Add or edit a vehicle: name, Bluetooth MAC address and picture."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return await self._async_step_vehicle(user_input, None)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return await self._async_step_vehicle(user_input, self._get_reconfigure_subentry())

    async def _async_step_vehicle(
        self, user_input: dict[str, Any] | None, subentry: ConfigSubentry | None
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            mac = user_input[CONF_MAC].strip().upper()
            if not MAC_PATTERN.match(mac):
                errors[CONF_MAC] = "invalid_mac"
            else:
                mac = mac.replace("-", ":")
                if any(d[CONF_MAC] == mac for d in self._others(subentry)):
                    errors[CONF_MAC] = "duplicate_mac"
            picture = user_input.get(CONF_PICTURE)
            if not errors and (file_id := user_input.get(CONF_PICTURE_FILE)):
                picture = await self.hass.async_add_executor_job(
                    save_picture, self.hass, file_id, mac.replace(":", "").lower()
                )
                if picture is None:
                    errors[CONF_PICTURE_FILE] = "invalid_image"
            if not errors:
                data = {CONF_NAME: user_input[CONF_NAME], CONF_MAC: mac, CONF_PICTURE: picture}
                return self._finish(subentry, data[CONF_NAME], data)

        suggested = user_input or (subentry.data if subentry else None)
        return self.async_show_form(
            step_id="reconfigure" if subentry else "user",
            data_schema=self.add_suggested_values_to_schema(VEHICLE_SCHEMA, suggested),
            errors=errors,
        )


class PersonSubentryFlow(_SubentryFlow):
    """Add or edit a person: a `person` entity and the phone's Bluetooth sensor."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return await self._async_step_person(user_input, None)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return await self._async_step_person(user_input, self._get_reconfigure_subentry())

    async def _async_step_person(
        self, user_input: dict[str, Any] | None, subentry: ConfigSubentry | None
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if any(d[CONF_PERSON] == user_input[CONF_PERSON] for d in self._others(subentry)):
                errors[CONF_PERSON] = "duplicate_person"
            else:
                state = self.hass.states.get(user_input[CONF_PERSON])
                title = state.name if state else user_input[CONF_PERSON]
                return self._finish(subentry, title, dict(user_input))

        suggested = user_input or (subentry.data if subentry else None)
        return self.async_show_form(
            step_id="reconfigure" if subentry else "user",
            data_schema=self.add_suggested_values_to_schema(PERSON_SCHEMA, suggested),
            errors=errors,
        )
