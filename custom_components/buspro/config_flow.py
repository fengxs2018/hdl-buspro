"""
Config flow for HDL Buspro integration.

Handles initial gateway setup (host/port) and device management via OptionsFlow.
"""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_DEVICES,
    CONF_DEVICE_TYPE,
    CONF_SUBNET_ID,
    CONF_DEVICE_ID,
    CONF_CHANNEL,
    CONF_SUBTYPE,
    DEVICE_TYPES,
    DEVICE_TYPE_LIGHT,
    DEVICE_TYPE_SWITCH,
    DEVICE_TYPE_BINARY_SENSOR,
    DEVICE_TYPE_SENSOR,
    DEVICE_TYPE_CLIMATE,
    BINARY_SENSOR_SUBTYPES,
    SENSOR_SUBTYPES,
)

_LOGGER = logging.getLogger(__name__)


class BusproConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for HDL Buspro gateway setup."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial gateway setup step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="HDL Buspro",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT): int,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return BusproOptionsFlow()


class BusproOptionsFlow(config_entries.OptionsFlow):
    """Handle the options flow for managing Buspro devices."""

    def __init__(self):
        """Initialize options flow."""
        self.devices = None

    def _ensure_devices_loaded(self):
        """Lazy load devices from config entry options."""
        if self.devices is None:
            self.devices = dict(self.config_entry.options.get(CONF_DEVICES, {}))

    def _get_device_display_name(self, device_key, device_config):
        """Get a human-readable display string for a device."""
        name = device_config.get("name", device_key)
        subnet = device_config[CONF_SUBNET_ID]
        device_id = device_config[CONF_DEVICE_ID]
        channel = device_config.get(CONF_CHANNEL)
        device_type = device_config[CONF_DEVICE_TYPE]

        if channel is not None:
            addr = f"{subnet}.{device_id}.{channel}"
        else:
            addr = f"{subnet}.{device_id}"

        return f"{name} ({device_type}, {addr})"

    async def async_step_init(self, user_input=None):
        """Show the main menu: add / remove / done."""
        self._ensure_devices_loaded()

        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_device()
            elif action == "remove":
                return await self.async_step_remove_device()
            elif action == "done":
                return self.async_create_entry(
                    title="",
                    data={CONF_DEVICES: self.devices},
                )

        # Build device list summary
        if self.devices:
            summary = "\n".join([
                f"  - {self._get_device_display_name(k, v)}"
                for k, v in self.devices.items()
            ])
        else:
            summary = "  (none)"

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("action"): vol.In({
                    "add": "Add device",
                    "remove": "Remove device",
                    "done": "Done",
                }),
            }),
            description_placeholders={"devices": summary},
        )

    async def async_step_add_device(self, user_input=None):
        """Step: select device type."""
        if user_input is not None:
            device_type = user_input[CONF_DEVICE_TYPE]
            if device_type == DEVICE_TYPE_LIGHT:
                return await self.async_step_add_light()
            elif device_type == DEVICE_TYPE_SWITCH:
                return await self.async_step_add_switch()
            elif device_type == DEVICE_TYPE_BINARY_SENSOR:
                return await self.async_step_add_binary_sensor()
            elif device_type == DEVICE_TYPE_SENSOR:
                return await self.async_step_add_sensor()
            elif device_type == DEVICE_TYPE_CLIMATE:
                return await self.async_step_add_climate()

        return self.async_show_form(
            step_id="add_device",
            data_schema=vol.Schema({
                vol.Required(CONF_DEVICE_TYPE): vol.In(DEVICE_TYPES),
            }),
        )

    async def async_step_add_light(self, user_input=None):
        """Step: add a light device."""
        if user_input is not None:
            subnet = user_input[CONF_SUBNET_ID]
            dev_id = user_input[CONF_DEVICE_ID]
            channel = user_input[CONF_CHANNEL]
            key = f"{DEVICE_TYPE_LIGHT}_{subnet}_{dev_id}_{channel}"

            self.devices[key] = {
                CONF_DEVICE_TYPE: DEVICE_TYPE_LIGHT,
                CONF_SUBNET_ID: subnet,
                CONF_DEVICE_ID: dev_id,
                CONF_CHANNEL: channel,
                "name": user_input.get("name", f"Light {subnet}-{dev_id}-{channel}"),
            }
            return await self.async_step_init()

        return self.async_show_form(
            step_id="add_light",
            data_schema=vol.Schema({
                vol.Required(CONF_SUBNET_ID): int,
                vol.Required(CONF_DEVICE_ID): int,
                vol.Required(CONF_CHANNEL): int,
                vol.Optional("name", default=""): str,
            }),
        )

    async def async_step_add_switch(self, user_input=None):
        """Step: add a switch device."""
        if user_input is not None:
            subnet = user_input[CONF_SUBNET_ID]
            dev_id = user_input[CONF_DEVICE_ID]
            channel = user_input[CONF_CHANNEL]
            key = f"{DEVICE_TYPE_SWITCH}_{subnet}_{dev_id}_{channel}"

            self.devices[key] = {
                CONF_DEVICE_TYPE: DEVICE_TYPE_SWITCH,
                CONF_SUBNET_ID: subnet,
                CONF_DEVICE_ID: dev_id,
                CONF_CHANNEL: channel,
                "name": user_input.get("name", f"Switch {subnet}-{dev_id}-{channel}"),
            }
            return await self.async_step_init()

        return self.async_show_form(
            step_id="add_switch",
            data_schema=vol.Schema({
                vol.Required(CONF_SUBNET_ID): int,
                vol.Required(CONF_DEVICE_ID): int,
                vol.Required(CONF_CHANNEL): int,
                vol.Optional("name", default=""): str,
            }),
        )

    async def async_step_add_binary_sensor(self, user_input=None):
        """Step: add a binary sensor device."""
        if user_input is not None:
            subnet = user_input[CONF_SUBNET_ID]
            dev_id = user_input[CONF_DEVICE_ID]
            channel = user_input[CONF_CHANNEL]
            subtype = user_input[CONF_SUBTYPE]
            key = f"{DEVICE_TYPE_BINARY_SENSOR}_{subnet}_{dev_id}_{channel}"

            self.devices[key] = {
                CONF_DEVICE_TYPE: DEVICE_TYPE_BINARY_SENSOR,
                CONF_SUBNET_ID: subnet,
                CONF_DEVICE_ID: dev_id,
                CONF_CHANNEL: channel,
                CONF_SUBTYPE: subtype,
                "name": user_input.get("name", f"Sensor {subnet}-{dev_id}-{channel}"),
            }
            return await self.async_step_init()

        return self.async_show_form(
            step_id="add_binary_sensor",
            data_schema=vol.Schema({
                vol.Required(CONF_SUBNET_ID): int,
                vol.Required(CONF_DEVICE_ID): int,
                vol.Required(CONF_CHANNEL): int,
                vol.Required(CONF_SUBTYPE): vol.In(BINARY_SENSOR_SUBTYPES),
                vol.Optional("name", default=""): str,
            }),
        )

    async def async_step_add_sensor(self, user_input=None):
        """Step: add a sensor device (no channel)."""
        if user_input is not None:
            subnet = user_input[CONF_SUBNET_ID]
            dev_id = user_input[CONF_DEVICE_ID]
            subtype = user_input[CONF_SUBTYPE]
            key = f"{DEVICE_TYPE_SENSOR}_{subnet}_{dev_id}"

            self.devices[key] = {
                CONF_DEVICE_TYPE: DEVICE_TYPE_SENSOR,
                CONF_SUBNET_ID: subnet,
                CONF_DEVICE_ID: dev_id,
                CONF_SUBTYPE: subtype,
                "name": user_input.get("name", f"Sensor {subnet}-{dev_id}"),
            }
            return await self.async_step_init()

        return self.async_show_form(
            step_id="add_sensor",
            data_schema=vol.Schema({
                vol.Required(CONF_SUBNET_ID): int,
                vol.Required(CONF_DEVICE_ID): int,
                vol.Required(CONF_SUBTYPE): vol.In(SENSOR_SUBTYPES),
                vol.Optional("name", default=""): str,
            }),
        )

    async def async_step_add_climate(self, user_input=None):
        """Step: add a climate device (no channel)."""
        if user_input is not None:
            subnet = user_input[CONF_SUBNET_ID]
            dev_id = user_input[CONF_DEVICE_ID]
            key = f"{DEVICE_TYPE_CLIMATE}_{subnet}_{dev_id}"

            self.devices[key] = {
                CONF_DEVICE_TYPE: DEVICE_TYPE_CLIMATE,
                CONF_SUBNET_ID: subnet,
                CONF_DEVICE_ID: dev_id,
                "name": user_input.get("name", f"Climate {subnet}-{dev_id}"),
            }
            return await self.async_step_init()

        return self.async_show_form(
            step_id="add_climate",
            data_schema=vol.Schema({
                vol.Required(CONF_SUBNET_ID): int,
                vol.Required(CONF_DEVICE_ID): int,
                vol.Optional("name", default=""): str,
            }),
        )

    async def async_step_remove_device(self, user_input=None):
        """Step: remove a device."""
        if user_input is not None:
            device_key = user_input.get("device")
            if device_key and device_key in self.devices:
                del self.devices[device_key]
            return await self.async_step_init()

        if not self.devices:
            return self.async_show_form(
                step_id="remove_device",
                data_schema=vol.Schema({}),
                description_placeholders={"message": "No devices to remove."},
            )

        device_options = {
            key: self._get_device_display_name(key, cfg)
            for key, cfg in self.devices.items()
        }

        return self.async_show_form(
            step_id="remove_device",
            data_schema=vol.Schema({
                vol.Required("device"): vol.In(device_options),
            }),
        )
