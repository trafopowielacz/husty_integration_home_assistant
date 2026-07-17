"""Config flow for Husty."""

from __future__ import annotations

import logging
from typing import Any, Mapping

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import (
    async_get_clientsession,
)
from homeassistant.helpers import selector

from .api import (
    HustyApiClient,
    HustyAuthenticationError,
    HustyConnectionError,
    HustyInvalidResponseError,
)
from .const import (
    CONF_API_KEY,
    DEVICE_URL,
    DOMAIN,
    REQUEST_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


API_KEY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): selector.TextSelector(
            selector.TextSelectorConfig(
                type=selector.TextSelectorType.PASSWORD,
                autocomplete="off",
            )
        )
    }
)


class HustyConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle the Husty config flow."""

    VERSION = 2
    MINOR_VERSION = 0

    async def _async_validate_api_key(
        self,
        api_key: str,
    ) -> dict[str, Any]:
        """Validate an API key and return the device."""

        session = async_get_clientsession(self.hass)

        client = HustyApiClient(
            session=session,
            api_key=api_key,
            device_url=DEVICE_URL,
            request_timeout=REQUEST_TIMEOUT,
        )

        return await client.async_get_device()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle initial setup."""

        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()

            try:
                device = await self._async_validate_api_key(
                    api_key
                )

            except HustyAuthenticationError:
                errors["base"] = "invalid_auth"

            except HustyConnectionError:
                errors["base"] = "cannot_connect"

            except HustyInvalidResponseError:
                errors["base"] = "invalid_response"

            except Exception:
                _LOGGER.exception(
                    "Nieoczekiwany błąd konfiguracji Husty"
                )
                errors["base"] = "unknown"

            else:
                device_id = device["deviceId"]
                metadata = device.get("metadata", {})

                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                title = (
                    metadata.get("modelName")
                    or "Husty"
                )

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_API_KEY: api_key,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=API_KEY_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, Any],
    ) -> FlowResult:
        """Start API key reauthentication."""

        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle replacement of an invalid API key."""

        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()

            try:
                device = await self._async_validate_api_key(
                    api_key
                )

            except HustyAuthenticationError:
                errors["base"] = "invalid_auth"

            except HustyConnectionError:
                errors["base"] = "cannot_connect"

            except HustyInvalidResponseError:
                errors["base"] = "invalid_response"

            except Exception:
                _LOGGER.exception(
                    "Nieoczekiwany błąd ponownej "
                    "autoryzacji Husty"
                )
                errors["base"] = "unknown"

            else:
                device_id = device["deviceId"]

                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_mismatch()

                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data_updates={
                        CONF_API_KEY: api_key,
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=API_KEY_SCHEMA,
            errors=errors,
        )
