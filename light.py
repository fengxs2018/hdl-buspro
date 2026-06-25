"""
This component provides light support for Buspro.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/...
"""

import logging

from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
)
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
    DEVICE_TYPE_LIGHT,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_DIMMABLE = True


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Buspro light devices from a config entry."""
    # noinspection PyUnresolvedReferences
    from .pybuspro.devices import Light

    buspro_module = hass.data[DOMAIN]
    hdl = buspro_module.hdl
    devices = config_entry.options.get(CONF_DEVICES, {})
    entities = []

    for device_key, device_config in devices.items():
        if device_config[CONF_DEVICE_TYPE] != DEVICE_TYPE_LIGHT:
            continue

        subnet_id = device_config[CONF_SUBNET_ID]
        device_id = device_config[CONF_DEVICE_ID]
        channel = device_config[CONF_CHANNEL]
        name = device_config.get("name", f"Light {subnet_id}-{device_id}-{channel}")
        device_address = (subnet_id, device_id)

        _LOGGER.debug(
            "Adding light '%s' with address %s and channel %s",
            name, device_address, channel
        )

        light = Light(hdl, device_address, channel, name)
        entities.append(BusproLight(hass, light, dimmable=True))

    async_add_entities(entities)


# noinspection PyAbstractClass
class BusproLight(LightEntity):
    """Representation of a Buspro light."""

    def __init__(self, hass, device, dimmable):
        self._hass = hass
        self._device = device
        self._dimmable = dimmable
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
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
        """Return the display name of this light."""
        return self._device.name

    @property
    def available(self):
        """Return True if entity is available."""
        return self._hass.data[DATA_BUSPRO].connected

    @property
    def brightness(self):
        """Return the brightness of the light."""
        brightness = self._device.current_brightness / 100 * 255
        return brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._device.is_on

    async def async_turn_on(self, **kwargs):
        """Instruct the light to turn on."""
        brightness = int(kwargs.get(ATTR_BRIGHTNESS, 255) / 255 * 100)

        if not self.is_on and self._device.previous_brightness is not None and brightness == 100:
            brightness = self._device.previous_brightness

        await self._device.set_brightness(brightness, 0)

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        await self._device.set_off(0)

    @property
    def unique_id(self):
        """Return the unique id."""
        return self._device.device_identifier
