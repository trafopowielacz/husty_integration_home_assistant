from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN


class HustyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Husty."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup."""

        if user_input is not None:
            return self.async_create_entry(
                title="Husty",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("email"): str,
                    vol.Required("password"): str,
                    vol.Required("device_id"): str,
                }
            ),
        )