"""Config flow for Essent Dynamic Pricing integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EssentDynamicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Essent Dynamic Pricing."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Essent Dynamic Pricing", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({})
        )
