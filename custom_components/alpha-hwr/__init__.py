from alpha_hwr import AlphaHWRClient
from alpha_hwr.models import TelemetryData

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
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Alpha HWR component from a config entry."""
    _LOGGER.debug("Setting up Alpha HWR component from config entry: %s", entry.data[CONF_NAME])

    client = CachingAlphaHWRClient(AlphaHWRClient(entry.data[CONF_ADDRESS]))
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    entry_data = hass.data[DOMAIN][entry.entry_id]

    if client := hass.data.pop(entry.entry_id, None):
        client.close()
    bluetooth.async_rediscover_address(hass, entry.data[CONF_ADDRESS])
    return True


class CachingAlphaHWRClient():
    """A wrapper around AlphaHWRClient that caches the latest values."""

    def __init__(self, core_client: AlphaHWRClient) -> None:
        self._core_client = core_client
        self._telemetry: TelemetryData = None
        self._last_update: datetime = None

    async def get_telemetry(self) -> TelemetryData:
        """Get the latest telemetry data, using the cache if available."""
        if self._telemetry is None or (datetime.now() - self._last_update).total_seconds() > DEFAULT_MIN_REFRESH_INTERVAL:
            try:
                self._telemetry = await self._core_client.telemetry.read_once()
                self._last_update = datetime.now()
            except Exception as e:
                _LOGGER.error("Error fetching telemetry data: %s", e)
                self._telemetry = None
        return self._telemetry