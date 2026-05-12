from bluetooth_data_tools import human_readable_name
from homeassistant import config_entries, exceptions
from homeassistant.const import (
    CONF_NAME,
    CONF_ADDRESS,
)
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.data_entry_flow import FlowResult

import logging
from typing import Any, Mapping
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Alpha HWR."""

    VERSION = 1
    name = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Integration must be set-up from auto-discovery")
        return self.async_abort(reason="no_devices_found")

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> FlowResult:
        """Handle the bluetooth discovery step."""
        _LOGGER.debug("Starting bluetooth step")

        self.address = discovery_info.address
        self.name = discovery_info.advertisement.local_name
        if not self.name:
            return self.async_abort(reason="")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {
            CONF_NAME: human_readable_name(
                None, discovery_info.name, discovery_info.address
            )
        }
        return self.async_show_form(step_id="setup")
    
    async def async_step_setup(self, user_input: Mapping[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(
                title=self.name or "",
                data={
                    CONF_ADDRESS: self.address,
                    CONF_NAME: self.name,
                },
            )
        return self.async_show_form(
            step_id="setup",
            description_placeholders={
                CONF_NAME: self.name,
            },
            last_step=True,
        )
