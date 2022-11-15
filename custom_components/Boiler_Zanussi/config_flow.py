from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from .const import DOMAIN  # pylint:disable=unused-import
from .boiler import Boiler

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({("username"): str, ("password"): str})


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    if len(data["username"]) < 3:
        raise InvalidUsername
    if len(data["password"]) < 3:
        raise InvalidPassword

    return {"title": data["username"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):

        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidUsername:
                errors["username"] = "invalid_username"
            except InvalidPassword:
                errors["password"] = "invalid_password"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class InvalidUsername(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidPassword(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""