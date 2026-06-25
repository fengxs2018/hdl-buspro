"""
This component provides binary sensor support for Buspro.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/...
"""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

from . import DATA_BUSPRO
from .const import (
    DOMAIN,
    CONF_DEVICES,
    CONF_DEVICE_TYPE,
    CONF_SUBNET_ID,
    CONF_DEVICE_ID,
    CONF_CHANNEL,
    CONF_SUBTYPE,
    DEVICE_TYPE_BINARY_SENSOR,
)

_LOGGER = logging.getLogger(__name__)

CONF_MOTION = 'motion'
CONF_DRY_CONTACT_1 = 'dry_contact_1'
CONF_DRY_CONTACT_2 = 'dry_contact_2'
CONF_UNIVERSAL_SWITCH = 'universal_switch'
CONF_SINGLE_CHANNEL = 'single_channel'
CONF_DRY_CONTACT = 'dry_contact'


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Buspro binary sensor devices from a config entry."""
    # noinspection PyUnresolvedReferences
    from .pybuspro.devices import Sensor

    buspro_module = hass.data[DOMAIN]
    hdl = buspro_module.hdl
    devices = config_entry.options.get(CONF_DEVICES, {})
    entities = []

    for device_key, device_config in devices.items():
        if device_config[CONF_DEVICE_TYPE] != DEVICE_TYPE_BINARY_SENSOR:
            continue

        subnet_id = device_config[CONF_SUBNET_ID]
        device_id = device_config[CONF_DEVICE_ID]
        sensor_type = device_config.get(CONF_SUBTYPE, CONF_MOTION)
        name = device_config.get("name", f"Sensor {subnet_id}-{device_id}")
        device_address = (subnet_id, device_id)

        universal_switch_number = None
        channel_number = None
        switch_number = None

        if sensor_type == CONF_UNIVERSAL_SWITCH:
            universal_switch_number = device_config.get(CONF_CHANNEL)
        elif sensor_type == CONF_SINGLE_CHANNEL:
            channel_number = device_config.get(CONF_CHANNEL)
        elif sensor_type == CONF_DRY_CONTACT:
            switch_number = device_config.get(CONF_CHANNEL)

        _LOGGER.debug(
            "Adding binary sensor '%s' with address %s, type '%s'",
            name, device_address, sensor_type
        )

        sensor = Sensor(
            hdl, device_address,
            universal_switch_number=universal_switch_number,
            channel_number=channel_number,
            switch_number=switch_number,
            name=name,
        )

        entities.append(BusproBinarySensor(hass, sensor, sensor_type, None))

    async_add_entities(entities)


# noinspection PyAbstractClass
class BusproBinarySensor(BinarySensorEntity):
    """Representation of a Buspro binary sensor."""

    def __init__(self, hass, device, sensor_type, device_class):
        self._hass = hass
        self._device = device
        self._device_class = device_class
        self._sensor_type = sensor_type
        self.async_register_callbacks()

    @callback
    def async_register_callbacks(self):
        """Register callbacks to update hass after device was changed."""

        # noinspection PyUnusedLocal
        async def after_update_callback(device):
            """Call after device was updated."""
            self.async_write_ha_state()

        self._device.register_device_updated_cb(after_update_callback)

    @property
    def should_poll(self):
        """No polling needed within Buspro."""
        return False

    async def async_update(self):
        if self._sensor_type == CONF_UNIVERSAL_SWITCH:
            await self._device.read_sensor_status()

    @property
    def name(self):
        """Return the display name of this binary sensor."""
        return self._device.name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._hass.data[DATA_BUSPRO].connected

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return self._device_class

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._device.device_identifier

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._sensor_type == CONF_MOTION:
            return self._device.movement
        if self._sensor_type == CONF_DRY_CONTACT_1:
            return self._device.dry_contact_1_is_on
        if self._sensor_type == CONF_DRY_CONTACT_2:
            return self._device.dry_contact_2_is_on
        if self._sensor_type == CONF_UNIVERSAL_SWITCH:
            return self._device.universal_switch_is_on
        if self._sensor_type == CONF_SINGLE_CHANNEL:
            return self._device.single_channel_is_on
        if self._sensor_type == CONF_DRY_CONTACT:
            return self._device.switch_status
        return False
