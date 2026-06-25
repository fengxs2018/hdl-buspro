# HDL Buspro

Home Assistant integration for [HDL Buspro](https://www.hdl.com.hk/) (河东智能家居) smart home system.

## Overview

This integration connects Home Assistant to the HDL Buspro system via a Buspro-to-IP gateway. It communicates over the local network using UDP multicast — no cloud connection required.

## Features

- **UI Configuration** — Add and manage devices through the Home Assistant UI, no YAML editing needed
- **Local Control** — All communication happens locally via UDP, no cloud dependency
- **Supported Platforms:**
  - **Light** — Dimmable lights with brightness control
  - **Switch** — On/off relay control
  - **Binary Sensor** — Motion, dry contact, universal switch, single channel
  - **Sensor** — Temperature and illuminance
  - **Climate** — Floor heating thermostat with preset modes
- **Services** — Activate scenes, send raw messages, control universal switches

## Requirements

- A HDL Buspro IP gateway (e.g. HDL-MULTI-PORT or similar) connected to your local network
- The gateway's IP address and port number (default port is usually 6000)
- Knowledge of your device addresses (Subnet ID, Device ID, Channel)

## Installation

### Via HACS (recommended)

1. Open HACS in Home Assistant
2. Go to **Integrations** → click the three dots menu → **Custom repositories**
3. Add `https://github.com/fengxs2018/hdl-buspro` as a new integration repository
4. Search for **HDL Buspro** and install

### Manual Installation

1. Copy the integration folder to your Home Assistant `custom_components` directory:
   ```
   config/custom_components/buspro/
   ```
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **HDL Buspro**
3. Enter the gateway's **IP address** and **port number**
4. Click **Submit**

### Adding Devices

After the integration is added, click **Configure** on the integration card to open the device management panel:

1. Select **Add device**
2. Choose the device type (light, switch, binary_sensor, sensor, or climate)
3. Enter the device address:
   - **Subnet ID** — The subnet number of the device
   - **Device ID** — The device number on the subnet
   - **Channel** — The channel number (not needed for sensor and climate)
   - **Name** — A friendly name for the entity
4. For binary sensors, also select the **sensor type** (motion, dry_contact, etc.)
5. For sensors, select the **sensor type** (temperature or illuminance)
6. Click **Submit**, then select **Done** when finished adding devices

### Device Address Format

HDL Buspro devices are addressed using three components:

| Component    | Description                          | Example |
|-------------|--------------------------------------|---------|
| Subnet ID   | The subnet number                    | 1       |
| Device ID   | The device number on that subnet     | 100     |
| Channel     | The output channel (lights/switches) | 9       |

You can find these addresses in the HDL device configuration software.

## Services

### `buspro.activate_scene`

Activate a scene on the bus.

| Field          | Description                        | Example    |
|---------------|------------------------------------|------------|
| `address`     | Device address as [subnet, device] | `[1, 74]`  |
| `scene_address` | Scene address as [area, scene]   | `[3, 5]`   |

### `buspro.send_message`

Send a raw Buspro message.

| Field          | Description                        | Example         |
|---------------|------------------------------------|-----------------|
| `address`     | Target device address              | `[1, 74]`       |
| `operate_code` | Operation code                    | `[4, 12]`       |
| `payload`     | Message payload                    | `[1, 75, 0, 3]` |

### `buspro.set_universal_switch`

Set a universal switch on/off.

| Field           | Description                    | Example    |
|----------------|-------------------------------|------------|
| `address`      | Device address                | `[1, 100]` |
| `switch_number` | Universal switch number       | `100`      |
| `status`       | 1 = on, 0 = off               | `1`        |

## Supported HDL Device Types

| Device              | Code   |
|--------------------|--------|
| SB_DN_6B0_10v      | 0x0011 |
| SB_DN_SEC250K      | 0x0BE9 |
| SB_CMS_12in1       | 0x0134 |
| SB_DN_Logic960     | 0x0453 |
| SB_DLP2            | 0x0086 |
| SB_DLP             | 0x0095 |
| SB_DLP_v2          | 0x009C |
| SB_WS8M            | 0x012B |
| SB_CMS_8in1        | 0x0135 |
| SB_DN_DT0601       | 0x0260 |
| HDL_MDT0601        | 0x026D |
| SB_DN_R0816        | 0x01AC |
| SB_DRY_4Z          | 0x0077 |
| HDL_MSP07M         | 0x0150 |

## Credits

- Original integration by [eyesoft](https://github.com/eyesoft/home_assistant_buspro)
- pybuspro protocol library bundled with this integration
- UI config flow added by [fengxs2018](https://github.com/fengxs2018)

## License

This project is provided as-is for the Home Assistant community.
