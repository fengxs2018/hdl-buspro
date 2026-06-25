DOMAIN = "buspro"

# Gateway configuration
CONF_HOST = "host"
CONF_PORT = "port"

# Device configuration keys
CONF_DEVICES = "devices"
CONF_DEVICE_TYPE = "device_type"
CONF_SUBNET_ID = "subnet_id"
CONF_DEVICE_ID = "device_id"
CONF_CHANNEL = "channel"
CONF_SUBTYPE = "subtype"

# Device types
DEVICE_TYPE_LIGHT = "light"
DEVICE_TYPE_SWITCH = "switch"
DEVICE_TYPE_BINARY_SENSOR = "binary_sensor"
DEVICE_TYPE_SENSOR = "sensor"
DEVICE_TYPE_CLIMATE = "climate"

DEVICE_TYPES = [
    DEVICE_TYPE_LIGHT,
    DEVICE_TYPE_SWITCH,
    DEVICE_TYPE_BINARY_SENSOR,
    DEVICE_TYPE_SENSOR,
    DEVICE_TYPE_CLIMATE,
]

# Binary sensor subtypes
BINARY_SENSOR_SUBTYPES = [
    "motion",
    "dry_contact_1",
    "dry_contact_2",
    "universal_switch",
    "single_channel",
    "dry_contact",
]

# Sensor subtypes
SENSOR_SUBTYPES = [
    "illuminance",
    "temperature",
]