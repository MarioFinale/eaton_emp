DOMAIN = "eaton_emp"

CONF_SERIAL_PORT = "serial_port"
CONF_SLAVE_ID = "slave_id"
CONF_NAME = "name"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_INVERT_DRY_CONTACTS = "invert_dry_contacts"
CONF_DRY_CONTACT_1_NAME = "dry_contact_1_name"      # ← NEW
CONF_DRY_CONTACT_2_NAME = "dry_contact_2_name"      # ← NEW
CONF_TEMP_UNIT = "temp_unit"                        # ← NEW

DEFAULT_SLAVE_ID = 1
DEFAULT_NAME = "Eaton Environmental Monitoring Probe"
DEFAULT_BAUDRATE = 19200
DEFAULT_PARITY = "E"
DEFAULT_STOPBITS = 1
DEFAULT_BYTESIZE = 8
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_INVERT_DRY_CONTACTS = False
DEFAULT_DRY_CONTACT_1_NAME = "Dry Contact 1"
DEFAULT_DRY_CONTACT_2_NAME = "Dry Contact 2"
DEFAULT_TEMP_UNIT = "Celsius"                       # ← NEW