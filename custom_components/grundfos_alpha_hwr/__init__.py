from alpha_hwr import AlphaHWRClient
from alpha_hwr.models import TelemetryData
import asyncio
from datetime import datetime

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_ADDRESS,
    Platform,
)
from homeassistant.core import HomeAssistant

import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_PLATFORMS = [
    Platform.SENSOR,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Alpha HWR component from a config entry."""
    _LOGGER.debug("Setting up Alpha HWR component from config entry: %s", entry.data[CONF_NAME])

    coordinator = AlphaHWRUpdateCoordinator(AlphaHWRClient(entry.data[CONF_ADDRESS]))
    await coordinator.client.connect()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, _PLATFORMS):
        return False

    if coordinator := hass.data[DOMAIN].pop(entry.entry_id, None):
        await coordinator.client.disconnect()
    bluetooth.async_rediscover_address(hass, entry.data[CONF_ADDRESS])
    return True

class AlphaHWRUpdateCoordinator:
    """Class to manage fetching data from the Alpha HWR client."""
    def __init__(self, client: AlphaHWRClient) -> None:
        self._lock = asyncio.Lock()
        self.client = client
        self.last_update = None

    async def get_telemetry(self) -> TelemetryData | None:
        """Fetch the latest telemetry data from the client."""
        async with self._lock:
            if self.last_update is None or (datetime.now() - self.last_update).total_seconds() > 5:
                await self.client.telemetry.read_once()
                self.last_update = datetime.now()
        return self.client.telemetry.current
