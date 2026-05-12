from homeassistant.components.sensor import (
	SensorEntity,
	SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    CONF_ADDRESS,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CachingAlphaHWRClient
from .const import DOMAIN


class AlphaHWRSensorEntity(SensorEntity):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._hass = hass
        self._entry = entry
        self._attr_native_value = None

    def _get_client(self) -> CachingAlphaHWRClient:
        """Get the Alpha HWR client from the Home Assistant data store."""
        return self._hass.data[DOMAIN][self._entry.entry_id]


class FlowRateSensorEntity(AlphaHWRSensorEntity):
    """Flow rate sensor for Grundfos Alpha HWR."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the flow rate sensor."""
        super().__init__(hass, entry)
        self._attr_name = f"{entry.data[CONF_NAME]} Flow Rate"
        self._attr_unique_id = f"{entry.data[CONF_ADDRESS]}_flow_rate"

        self._attr_native_unit_of_measurement = UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
        self._attr_suggested_display_precision = 1
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.FLOW

    async def async_update(self) -> None:
        """Fetch the latest flow rate from the client."""
        telemetry = await self._get_client().get_telemetry()
        if telemetry is not None:
            self._attr_native_value = telemetry.flow_m3h

class TempSensorEntity(AlphaHWRSensorEntity):
    """Temperature sensor for Grundfos Alpha HWR."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the temperature sensor."""
        super().__init__(hass, entry)
        self._attr_name = f"{entry.data[CONF_NAME]} Temperature"
        self._attr_unique_id = f"{entry.data[CONF_ADDRESS]}_temperature"

        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_suggested_display_precision = 1
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_device_class = SensorDeviceClass.TEMPERATURE

    async def async_update(self) -> None:
        """Fetch the latest temperature from the client."""
        telemetry = await self._get_client().get_telemetry()
        if telemetry is not None:
            self._attr_native_value = telemetry.media_temperature_c