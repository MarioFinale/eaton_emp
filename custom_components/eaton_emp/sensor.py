from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import EatonEmpCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: EatonEmpCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        EatonEmpTemperatureSensor(coordinator),
        EatonEmpHumiditySensor(coordinator),
    ])


class EatonEmpTemperatureSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: EatonEmpCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_temperature" 

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.coordinator.entry_id)}, "name": self.coordinator.device_name, "manufacturer": "Eaton", "model": "EMPDT1H1C2"}

    @property
    def native_unit_of_measurement(self):
        return UnitOfTemperature.FAHRENHEIT if self.coordinator.temp_unit == "Fahrenheit" else UnitOfTemperature.CELSIUS

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get("temperature")
        if value is None:
            return None
        if self.coordinator.temp_unit == "Fahrenheit":
            return round(value * 1.8 + 32, 1)
        return round(value, 2)   # keep 2 decimals in °C


class EatonEmpHumiditySensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: EatonEmpCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry_id}_humidity" 

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.coordinator.entry_id)}, "name": self.coordinator.device_name, "manufacturer": "Eaton", "model": "EMPDT1H1C2"}

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get("humidity")