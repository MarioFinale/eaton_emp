import asyncio
import logging
from datetime import timedelta

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.framer import FramerType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_INVERT_DRY_CONTACTS,
    CONF_DRY_CONTACT_1_NAME,
    CONF_DRY_CONTACT_2_NAME,
    CONF_TEMP_UNIT,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_PARITY,
    DEFAULT_STOPBITS,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_INVERT_DRY_CONTACTS,
    DEFAULT_DRY_CONTACT_1_NAME,
    DEFAULT_DRY_CONTACT_2_NAME,
    DEFAULT_TEMP_UNIT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eaton EMP from a config entry."""
    serial_port = entry.data[CONF_SERIAL_PORT]
    slave_id = entry.data[CONF_SLAVE_ID]

    device_name = entry.options.get(CONF_NAME, DEFAULT_NAME)
    update_interval_sec = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    invert_dry = entry.options.get(CONF_INVERT_DRY_CONTACTS, DEFAULT_INVERT_DRY_CONTACTS)
    dc1_name = entry.options.get(CONF_DRY_CONTACT_1_NAME, DEFAULT_DRY_CONTACT_1_NAME)
    dc2_name = entry.options.get(CONF_DRY_CONTACT_2_NAME, DEFAULT_DRY_CONTACT_2_NAME)
    temp_unit = entry.options.get(CONF_TEMP_UNIT, DEFAULT_TEMP_UNIT)

    if DOMAIN + "_locks" not in hass.data:
        hass.data[DOMAIN + "_locks"] = {}
    lock = hass.data[DOMAIN + "_locks"].setdefault(serial_port, asyncio.Lock())

    client = AsyncModbusSerialClient(
        framer=FramerType.RTU,
        port=serial_port,
        baudrate=DEFAULT_BAUDRATE,
        parity=DEFAULT_PARITY,
        stopbits=DEFAULT_STOPBITS,
        bytesize=DEFAULT_BYTESIZE,
        timeout=3,
    )

    coordinator = EatonEmpCoordinator(
        hass=hass,
        client=client,
        slave_id=slave_id,
        update_interval_sec=update_interval_sec,
        device_name=device_name,
        invert_dry_contacts=invert_dry,
        dry_contact_1_name=dc1_name,
        dry_contact_2_name=dc2_name,
        temp_unit=temp_unit,
        entry_id=entry.entry_id,
        lock=lock,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: EatonEmpCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        coordinator.client.close()
    return unload_ok


class EatonEmpCoordinator(DataUpdateCoordinator):
    """Coordinator for polling the Eaton EMP."""

    def __init__(
        self,
        hass: HomeAssistant,
        client,
        slave_id: int,
        update_interval_sec: int,
        device_name: str,
        invert_dry_contacts: bool,
        dry_contact_1_name: str,
        dry_contact_2_name: str,
        temp_unit: str,
        entry_id: str,
        lock: asyncio.Lock,
    ) -> None:
        self.client = client
        self.slave_id = slave_id
        self.device_name = device_name
        self.invert_dry_contacts = invert_dry_contacts
        self.dry_contact_1_name = dry_contact_1_name
        self.dry_contact_2_name = dry_contact_2_name
        self.temp_unit = temp_unit
        self.lock = lock

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_sec),
        )
        self.entry_id = entry_id

    async def _async_update_data(self) -> dict:
        """Fetch data from the device."""
        async with self.lock:
            await self.client.connect()
            if not self.client.connected:
                raise UpdateFailed("Failed to connect to serial port")

            try:
                data = {}

                # Temperature (Input Register 5)
                resp = await self.client.read_input_registers(
                    address=5, count=1, device_id=self.slave_id
                )
                if not resp.isError():
                    data["temperature"] = resp.registers[0] * 0.001

                # Humidity (Input Register 10)
                resp = await self.client.read_input_registers(
                    address=10, count=1, device_id=self.slave_id
                )
                if not resp.isError():
                    data["humidity"] = resp.registers[0] * 0.1

                # Dry Contact 1 (Discrete Input 0)
                resp = await self.client.read_discrete_inputs(
                    address=0, count=1, device_id=self.slave_id
                )
                if not resp.isError():
                    value = resp.bits[0]
                    data["dry_contact_1"] = not value if self.invert_dry_contacts else value

                # Dry Contact 2 (Discrete Input 1)
                resp = await self.client.read_discrete_inputs(
                    address=1, count=1, device_id=self.slave_id
                )
                if not resp.isError():
                    value = resp.bits[0]
                    data["dry_contact_2"] = not value if self.invert_dry_contacts else value

                return data

            finally:
                self.client.close()