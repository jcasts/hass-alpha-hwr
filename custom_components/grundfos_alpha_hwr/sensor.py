from alpha_hwr import AlphaHWRClient
from alpha_hwr.models import TelemetryData

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

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors for the Alpha HWR component."""
    entities = [
        FlowRateSensorEntity(hass, entry),
        WaterTempSensorEntity(hass, entry),
        PcbTempSensorEntity(hass, entry),
    ]

    async_add_entities(entities)

class AlphaHWRSensorEntity(SensorEntity):
    def __init__(
        self, hass: HomeAssistant,
        entry: ConfigEntry,
        sensor_type: str,
        native_unit_of_measurement: str,
        device_class: SensorDeviceClass,
        fn_telemetry: callable[[TelemetryData], float],
    ) -> None:
        self._hass = hass
        self._entry = entry
        self._attr_native_value = None
        self._attr_suggested_display_precision = 1
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_device_class = device_class
        self._attr_name = f"{entry.data[CONF_NAME]} {sensor_type}"
        self._attr_unique_id = f"{entry.data[CONF_ADDRESS]}_{'_'.join(sensor_type.lower().split())}"
        self._fn_telemetry = fn_telemetry

    async def async_update(self) -> None:
        """Fetch the latest temperature from the client."""
        telemetry = self._get_telemetry()
        if telemetry is not None:
            self._attr_native_value = self._fn_telemetry(telemetry)

    def _get_client(self) -> AlphaHWRClient:
        """Get the Alpha HWR client from the Home Assistant data store."""
        return self._hass.data[DOMAIN][self._entry.entry_id]
    
    def _get_telemetry(self) -> TelemetryData | None:
        """Get the latest telemetry data from the client."""
        client = self._get_client()
        telemetry = client.telemetry
        if telemetry is None:
            return None
        return client.telemetry.current


class FlowRateSensorEntity(AlphaHWRSensorEntity):
    """Flow rate sensor for Grundfos Alpha HWR."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the flow rate sensor."""
        super().__init__(
            hass,
            entry,
            "Flow Rate",
            UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
            SensorDeviceClass.FLOW,
            lambda telemetry: telemetry.flow_m3h)


class WaterTempSensorEntity(AlphaHWRSensorEntity):
    """Water temperature sensor for Grundfos Alpha HWR."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the water temperature sensor."""
        super().__init__(
            hass,
            entry,
            "Water Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            lambda telemetry: telemetry.media_temperature_c)


class PcbTempSensorEntity(AlphaHWRSensorEntity):
    """PCB temperature sensor for Grundfos Alpha HWR."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the PCB temperature sensor."""
        super().__init__(
            hass,
            entry,
            "PCB Temperature",
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            lambda telemetry: telemetry.pcb_temperature_c)
