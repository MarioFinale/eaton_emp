import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient
from pymodbus.framer import FramerType
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.config_entries import ConfigEntry, OptionsFlow

from .const import (
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_INVERT_DRY_CONTACTS,
    CONF_DRY_CONTACT_1_NAME,
    CONF_DRY_CONTACT_2_NAME,
    CONF_TEMP_UNIT,
    DEFAULT_SLAVE_ID,
    DEFAULT_NAME,
    DEFAULT_BAUDRATE,
    DEFAULT_PARITY,
    DEFAULT_STOPBITS,
    DEFAULT_BYTESIZE,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_INVERT_DRY_CONTACTS,
    DEFAULT_DRY_CONTACT_1_NAME,
    DEFAULT_DRY_CONTACT_2_NAME,
    DEFAULT_TEMP_UNIT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eaton EMP."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input.get(CONF_NAME, DEFAULT_NAME)
            if self._name_exists(name):
                errors["base"] = "name_already_used"
            else:
                try:
                    await self._test_connection(user_input)
                    data = {
                        CONF_SERIAL_PORT: user_input[CONF_SERIAL_PORT],
                        CONF_SLAVE_ID: user_input[CONF_SLAVE_ID],
                    }
                    options = {
                        CONF_NAME: name,
                        CONF_UPDATE_INTERVAL: user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                        CONF_INVERT_DRY_CONTACTS: user_input.get(CONF_INVERT_DRY_CONTACTS, DEFAULT_INVERT_DRY_CONTACTS),
                        CONF_DRY_CONTACT_1_NAME: user_input.get(CONF_DRY_CONTACT_1_NAME, DEFAULT_DRY_CONTACT_1_NAME),
                        CONF_DRY_CONTACT_2_NAME: user_input.get(CONF_DRY_CONTACT_2_NAME, DEFAULT_DRY_CONTACT_2_NAME),
                        CONF_TEMP_UNIT: user_input.get(CONF_TEMP_UNIT, DEFAULT_TEMP_UNIT),
                    }
                    return self.async_create_entry(
                        title=name,
                        data=data,
                        options=options,
                    )
                except ConnectionError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SERIAL_PORT): str,
                    vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
                        vol.Coerce(int), vol.Range(min=5, max=300)
                    ),
                    vol.Optional(CONF_INVERT_DRY_CONTACTS, default=DEFAULT_INVERT_DRY_CONTACTS): bool,
                    vol.Optional(CONF_DRY_CONTACT_1_NAME, default=DEFAULT_DRY_CONTACT_1_NAME): str,
                    vol.Optional(CONF_DRY_CONTACT_2_NAME, default=DEFAULT_DRY_CONTACT_2_NAME): str,
                    vol.Optional(CONF_TEMP_UNIT, default=DEFAULT_TEMP_UNIT): vol.In(["Celsius", "Fahrenheit"]),
                }
            ),
            errors=errors,
        )

    def _name_exists(self, name: str) -> bool:
        """Check if name is already used by another entry."""
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.options.get(CONF_NAME) == name:
                return True
        return False

    async def _test_connection(self, data: dict[str, Any]) -> None:
        """Test connection to the probe."""
        client = AsyncModbusSerialClient(
            framer=FramerType.RTU,
            port=data[CONF_SERIAL_PORT],
            baudrate=DEFAULT_BAUDRATE,
            parity=DEFAULT_PARITY,
            stopbits=DEFAULT_STOPBITS,
            bytesize=DEFAULT_BYTESIZE,
            timeout=3,
        )
        await client.connect()
        if not client.connected:
            raise ConnectionError("Failed to connect to serial port")
        try:
            # Test read temperature register
            response = await client.read_input_registers(
                address=5, count=1, device_id=data[CONF_SLAVE_ID]
            )
            if response.isError():
                raise ConnectionError("Modbus read error")
        finally:
            client.close()

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Eaton EMP."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        super().__init__(config_entry)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input.get(CONF_NAME, self.config_entry.options.get(CONF_NAME, DEFAULT_NAME))
            if name != self.config_entry.options.get(CONF_NAME) and self._name_exists(name):
                errors["base"] = "name_already_used"
            else:
                return self.async_create_entry(title="", data=user_input)

        current_name = self.config_entry.options.get(CONF_NAME, DEFAULT_NAME)
        current_interval = self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        current_invert = self.config_entry.options.get(CONF_INVERT_DRY_CONTACTS, DEFAULT_INVERT_DRY_CONTACTS)
        current_dc1 = self.config_entry.options.get(CONF_DRY_CONTACT_1_NAME, DEFAULT_DRY_CONTACT_1_NAME)
        current_dc2 = self.config_entry.options.get(CONF_DRY_CONTACT_2_NAME, DEFAULT_DRY_CONTACT_2_NAME)
        current_temp_unit = self.config_entry.options.get(CONF_TEMP_UNIT, DEFAULT_TEMP_UNIT)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=current_name): str,
                    vol.Optional(CONF_UPDATE_INTERVAL, default=current_interval): vol.All(
                        vol.Coerce(int), vol.Range(min=5, max=300)
                    ),
                    vol.Optional(CONF_INVERT_DRY_CONTACTS, default=current_invert): bool,
                    vol.Optional(CONF_DRY_CONTACT_1_NAME, default=current_dc1): str,
                    vol.Optional(CONF_DRY_CONTACT_2_NAME, default=current_dc2): str,
                    vol.Optional(CONF_TEMP_UNIT, default=current_temp_unit): vol.In(["Celsius", "Fahrenheit"]),
                }
            ),
            errors=errors,
        )

    def _name_exists(self, name: str) -> bool:
        """Check if name is already used by another entry."""
        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.entry_id != self.config_entry.entry_id and entry.options.get(CONF_NAME) == name:
                return True
        return False