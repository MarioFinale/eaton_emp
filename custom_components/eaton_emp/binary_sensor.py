from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import EatonEmpCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: EatonEmpCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        EatonEmpDryContactSensor(coordinator, 1),
        EatonEmpDryContactSensor(coordinator, 2),
    ])

class EatonEmpDryContactSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: EatonEmpCoordinator, index: int) -> None:
        super().__init__(coordinator)
        self._index = index
        if index == 1:
            self._attr_name = coordinator.dry_contact_1_name
        else:
            self._attr_name = coordinator.dry_contact_2_name
        self._attr_unique_id = f"{self.coordinator.entry_id}_dry_contact_{index}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry_id)},
            "name": self.coordinator.device_name,
            "manufacturer": "Eaton",
            "model": "EMPDT1H1C2",
        }

    @property
    def is_on(self) -> bool | None:
        key = f"dry_contact_{self._index}"
        value = self.coordinator.data.get(key)
        if value is None:
            return None
        return not value if self.coordinator.invert_dry_contacts else value