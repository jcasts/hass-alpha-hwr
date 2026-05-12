from alpha_hwr import AlphaHWRClient

from datetime import datetime

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import (
    BluetoothChange,
    BluetoothServiceInfoBleak
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_ADDRESS,
    Platform,
)
from homeassistant.core import HomeAssistant

import logging

from .const import DEFAULT_MIN_REFRESH_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

_PLATFORMS = [
    Platform.SENSOR,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Alpha HWR component from a config entry."""
    _LOGGER.debug("Setting up Alpha HWR component from config entry: %s", entry.data[CONF_NAME])

    client = AlphaHWRClient(entry.data[CONF_ADDRESS])
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    if client := hass.data[DOMAIN].pop(entry.entry_id, None):
        client.disconnect()
    bluetooth.async_rediscover_address(hass, entry.data[CONF_ADDRESS])
    return True
