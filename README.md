# Bruciatore_BLE Controller

This project provides a Python script for interacting with the VEVOR diesel air heater, All-in-One model, via Bluetooth Low Energy (BLE). The code has been developed through Bluetooth data sniffing between the heater and the manufacturer's "AirHeaterBLE" app.

## Description

The VEVOR diesel air heater is designed for use in cars, campers, trucks, and RVs. This script allows you to control the heater using a BLE-compatible device, such as a Raspberry Pi or a computer with a Bluetooth adapter.

## Features

- Bluetooth Low Energy connection with the VEVOR Diesel Air Heater device.
- Sending specific commands (cmd1-19) to control various heater functionalities.
- Monitoring and displaying information received from the heater, such as temperature, ignition status, power, and more.

## Requirements

- Python 3.x
- Bluepy Library: `pip install bluepy`

## Usage

1. Ensure your Bluetooth device is enabled.
2. Run the Python script.
3. Follow the instructions to input manual commands or let the script automatically send the `cmd1` command at regular intervals.

## Supported Commands

- `cmd10`: Turns on the heater.
- `cmd8`: Turns off the heater.
- Other commands: Adjust power, temperature, and other heater features.

## Product Information

For more details about the VEVOR Diesel Air Heater, visit the [VEVOR product page](https://www.vevor.it/riscaldatore-aria-diesel-c_10321/vevor-riscaldatore-d-aria-diesel-all-in-one-per-auto-camper-camion-rv-12v-5kw-temperatura-regolabile-8-36-controllo-bluetooth-riscaldatore-da-parcheggio-per-auto-consumo-di-carburante-0-16-0-52l-h-p_010971160616).

## Important Note

This project is created for educational purposes and automation of the VEVOR diesel air heater. Use the software at your own risk. The author is not responsible for any damage resulting from the improper use of the code.
For a more comprehensive understanding of the utilized protocol, refer to the detailed explanation available at [this link](https://github.com/iotmaestro/vevor-heater-ble).
