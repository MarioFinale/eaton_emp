# Eaton EMP – Home Assistant Integration

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/MarioFinale/eaton-emp)](https://github.com/MarioFinale/eaton-emp/releases)
[![License](https://img.shields.io/github/license/MarioFinale/eaton-emp)](LICENSE)

<p align="center">
  <img src="https://dynamicmedia.eaton.com/is/image/eaton/EMPDT1H1C2_R" width="320" alt="Eaton Environmental Monitoring Probe Gen 2">
</p>

Custom Home Assistant integration for the **Eaton Environmental Monitoring Probe Gen 2 (EMPDT1H1C2)** using Modbus RTU over USB.

## Features
- Real-time **Temperature** sensor (0–70 °C) with optional °F display
- Real-time **Relative Humidity** sensor (0-90 %RH)
- Two **Dry Contact** binary sensors (door switches, alarms, etc.) with custom names and optional inversion
- Full UI configuration — **no YAML required**
- Configurable polling interval (5–300 seconds)
- Support for multiple daisy-chained probes
- Read-only (safe for monitoring only)

## Supported Devices
- Eaton Environmental Monitoring Probe Gen 2 (**EMPDT1H1C2**)
- Any clone/compatible probe using the same Modbus register map

## Important Notes & Disclaimer

The Eaton Environmental Monitoring Probe Gen 2 is **officially designed** to work with Eaton UPS systems, PDUs, and Network Management Cards.

This integration was created through **reverse engineering** and allows you to connect the probe **directly to any computer running Home Assistant** using the supplied USB cable — no Eaton UPS or PDU is required for basic monitoring.

**Please note:**
- This integration is **read-only** — it can only read sensor values. It cannot write, configure, or update the probe.
- For firmware updates, calibration, or any advanced configuration you will need an official Eaton UPS, PDU, or Network Management Card.

Use at your own risk!

> There is **no official warranty or support** from Eaton when used directly with Home Assistant.

## Finding the Correct Serial Port (Important!)

**Important:** Make sure you are using the original Eaton USB cable that came with the probe. This cable contains the built-in USB-to-serial converter (FT232R) needed to communicate with the first probe in the chain.

### How to find the correct path:
1. Go to **Settings → Devices & Services → Hardware** (click the **All Hardware** tab)
2. In the search box, type `ttyUSB` or `FT232`
3. Find the device whose **Model** or **Description** contains `FT232R_USB_UART`
4. Click on it and copy the full path in the **Attributes** section that starts with:
```
/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_...
```
**Why use the `/dev/serial/by-id/...` path instead of `/dev/ttyUSB0`?**  
The simple `/dev/ttyUSB0` name can change after a reboot, when you unplug/replug devices, or when other USB devices are connected. The `by-id` path is permanent and always points to the exact same physical probe using its unique hardware ID. This is especially important when you have multiple probes or other USB devices on your system.

> **Note**: Only the first probe in the chain is connected via this USB cable. All other probes connect via standard RJ45 patch cables.

## Configuration
1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Eaton Environmental Monitoring Probe**
3. Enter:
- **Serial Port**: the full `/dev/serial/by-id/...` path (strongly recommended)
- **Slave ID**: `1` (default — set via DIP switches on each probe)
4. Click Submit

After setup, click **Options** on the integration card to customize name, dry contact names, inversion, temperature unit, and polling interval.

## Multiple Probes / Daisy-Chained Network

The Eaton EMP uses **RS-485 daisy-chaining** via standard RJ45 patch cords:

- Only **one USB cable** is plugged into your Home Assistant machine (connected to the first probe).
- Additional probes are connected to each other with RJ45 cables.
- Each probe must have a **unique Slave ID** (configured via its DIP switches).

In Home Assistant you simply add multiple instances of the integration:
- All instances use the **same serial port** (`/dev/serial/by-id/...`)
- Each instance uses a **different Slave ID**

## Entities Created
| Entity ID                          | Type           | Description                     |
|------------------------------------|----------------|---------------------------------|
| `sensor.eaton_emp_temperature`     | Sensor         | Ambient temperature (°C or °F)  |
| `sensor.eaton_emp_humidity`        | Sensor         | Relative humidity (%RH)         |
| `binary_sensor.eaton_emp_dry_contact_1` | Binary Sensor | Dry contact input 1             |
| `binary_sensor.eaton_emp_dry_contact_2` | Binary Sensor | Dry contact input 2             |

## Troubleshooting
- **Integration doesn't appear**: Restart HA twice after placing files
- **"Cannot connect"**: Use the full `/dev/serial/by-id/...` path. Make sure the original Eaton USB cable is connected securely and that you are not using a USB extender that is too long.
- **No values / wrong values**: Confirm each probe’s Slave ID with a Modbus tool
- **Dry contacts wrong state**: Go to integration → **Options** → toggle “Invert Dry Contact Logic”
- **Want custom names or °F**: Go to integration → **Options**
- Check logs: `Settings → System → Logs` and filter for `eaton_emp`

## Credits & Thanks
- Built with assistance from Grok (xAI). I really, really hate python!
- Uses `pymodbus` for reliable Modbus RTU communication

## Contributing

Pull requests are **welcome and greatly appreciated**!

### Guidelines

- **One change at a time** — Please keep pull requests small and focused on a single feature or fix. Large PRs that modify many files at once are much harder to review.
- **AI-assisted code** — If you used any AI tool (Grok, ChatGPT, Claude, Copilot, etc.) to help write or generate code, please clearly mention it in the PR description.  
  Also, please wait until any existing PRs are reviewed/merged before opening new ones — I’m only one human with limited time.
- **Read-only only** — **Do not add any write features** (coils, holding registers, configuration writes, etc.).  
  This integration is intentionally read-only. The probe was designed to work with Eaton UPS/PDUs, and writing values could potentially cause problems or bring unwanted attention to the project.

### How to contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-awesome-change`)
3. Make your changes
4. Test them with real hardware if possible
5. Open a Pull Request with a clear description

Feel free to open an **Issue** first if you want to discuss a bigger idea or need guidance.

Thank you for helping make this integration better!

## License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute it as you wish.

Full license text: [LICENSE](LICENSE)

---

Made with ❤️ for the Home Assistant community.
