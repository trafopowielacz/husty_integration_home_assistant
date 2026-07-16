"""Config flow for Husty."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .api import (
    HustyApiClient,
    HustyAuthenticationError,
    HustyConnectionError,
    HustyInvalidResponseError,
)
from .const import (
    CONF_DEVICE_ID,
    CONF_EMAIL,
    CONF_PASSWORD,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DEVICE_ID): str,
    }
)


class HustyConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for Husty."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial setup step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL].strip().lower()
            password = user_input[CONF_PASSWORD]
            device_id = user_input[CONF_DEVICE_ID].strip()

            api = HustyApiClient(
                email=email,
                password=password,
                device_id=device_id,
            )

            try:
                data = await api.async_get_data()

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
                device = data.get("device", {})
                core = device.get("core", {})

                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=core.get("model") or "Husty",
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: password,
                        CONF_DEVICE_ID: device_id,
                    },
                )

            finally:
                await api.async_close()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )
