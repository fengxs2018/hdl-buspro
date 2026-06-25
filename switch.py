"""
This component provides switch support for Buspro.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/...
"""

import logging

from homeassistant.components.switch import SwitchEntity
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
    DEVICE_TYPE_SWITCH,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Buspro switch devices from a config entry."""
    # noinspection PyUnresolvedReferences
    from .pybuspro.devices import Switch

    buspro_module = hass.data[DOMAIN]
    hdl = buspro_module.hdl
    devices = config_entry.options.get(CONF_DEVICES, {})
    entities = []

    for device_key, device_config in devices.items():
        if device_config[CONF_DEVICE_TYPE] != DEVICE_TYPE_SWITCH:
            continue

        subnet_id = device_config[CONF_SUBNET_ID]
        device_id = device_config[CONF_DEVICE_ID]
        channel = device_config[CONF_CHANNEL]
        name = device_config.get("name", f"Switch {subnet_id}-{device_id}-{channel}")
        device_address = (subnet_id, device_id)

        _LOGGER.debug(
            "Adding switch '%s' with address %s and channel %s",
            name, device_address, channel
        )

        switch = Switch(hdl, device_address, channel, name)
        entities.append(BusproSwitch(hass, switch))

    async_add_entities(entities)


# noinspection PyAbstractClass
class BusproSwitch(SwitchEntity):
    """Representation of a Buspro switch."""

    def __init__(self, hass, device):
        self._hass = hass
        self._device = device
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

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._device.name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._hass.data[DATA_BUSPRO].connected

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the switch to turn on."""
        await self._device.set_on()

    async def async_turn_off(self, **kwargs):
        """Instruct the switch to turn off."""
        await self._device.set_off()

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._device.device_identifier
