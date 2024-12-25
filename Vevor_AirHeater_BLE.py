import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, List
from bluepy.btle import Peripheral, DefaultDelegate
import threading
import time
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

# Enumerator definitions
class HeaterMode(IntEnum):
    LEVEL = 0x01
    AUTOMATIC = 0x02

class HeaterPower(IntEnum):
    OFF = 0x00
    ON = 0x01

class HeaterCommand(IntEnum):
    STATUS = 0x01
    MODE = 0x02
    POWER = 0x03
    LEVEL_OR_TEMP = 0x04

@dataclass
class HeaterStatus:
    power: bool
    mode: HeaterMode
    temperature: int
    target_temperature_level: int
    level: int
    running_state: int
    altitude: int
    voltage_battery: float
    temp_heating: int
    temp_room: int
    error_code: int

    def __str__(self) -> str:
         # Mappa dei valori di running_state a descrizioni testuali
        running_state_map = {
        0x00: "Warmup",
        0x01: "Self test running",
        0x02: "Ignition",
        0x03: "Heating",
        0x04: "Shutting down",
        }

        # Ottieni la descrizione testuale o un valore di default se non è valido
        running_state_description = running_state_map.get(self.running_state, "Unknown state")

        return (
            f"Power: {'ON' if self.power else 'OFF'}\n"
            f"Mode: {'AUTOMATIC' if self.mode == HeaterMode.AUTOMATIC else 'LEVEL'}\n"
            f"Current Temperature: {self.temp_room}°C\n"
            f"Target: {self.target_temperature_level}{'°C' if self.mode == HeaterMode.AUTOMATIC else ' (level)'}\n"
            f"Heating Temperature: {self.temp_heating}°C\n"
            f"Battery: {self.voltage_battery:.1f}V\n"
            f"Altitude: {self.altitude}m\n"
            f"Running state: {running_state_description}\n"
            f"Status Code: {self.error_code}"
        )

class VEVORHeater:
    HEADER = bytearray([0xAA, 0x55])
    SERVICE_UUID = "0000FFE0-0000-1000-8000-00805F9B34FB"
    CHAR_UUID = "0000FFE1-0000-1000-8000-00805F9B34FB"

    class NotificationDelegate(DefaultDelegate):
        def __init__(self, heater, console: Console):
            super().__init__()
            self.heater = heater
            self.console = console
            self.last_update = None

        def handleNotification(self, cHandle, data):
            """Handle BLE device notifications"""
            try:
                if data[0] == 170:
                    status = HeaterStatus(
                        power=bool(data[3]),
                        mode=HeaterMode.AUTOMATIC if data[8] == 2 else HeaterMode.LEVEL,
                        temperature=data[13] | (data[14] << 8),
                        target_temperature_level=data[9],
                        level=data[10],
                        running_state=data[5],
                        altitude=data[6] | (data[7] << 8),
                        voltage_battery=(data[11] | (data[12] << 8)) / 10,
                        temp_heating=data[13] | (data[14] << 8),
                        temp_room=data[15] | (data[16] << 8),
                        error_code=data[17]
                    )
                    
                    self.display_status(status)
                    
            except Exception as e:
                self.console.print(f"[red]Error processing notification: {e}[/red]")
        #####
        def display_status(self, status: HeaterStatus):
            """Display formatted status using Rich"""
            current_time = time.time()
            if self.last_update and current_time - self.last_update < 1:
                return
            
            self.last_update = current_time
            
            # Mappa dei running state
            running_state_map = {
                0x00: "Warmup",
                0x01: "Self test running",
                0x02: "Ignition",
                0x03: "Heating",
                0x04: "Shutting down",
            }
            
            # Ottieni la descrizione del running state
            running_state_description = running_state_map.get(status.running_state, "Unknown state")
            
            os.system('cls' if os.name == 'nt' else 'clear')
            
            layout = Layout()
            layout.split_column(
                Layout(name="status"),
                Layout(name="commands")
            )
            
            # Create status table with header as first row
            status_table = Table(show_header=False, box=None)
            status_table.add_row(
                f"[bold blue]VEVOR Heater Control - {datetime.now().strftime('%H:%M:%S')}[/bold blue]"
            )
            status_table.add_row("Power", "[green]ON[/green]" if status.power else "[red]OFF[/red]")
            status_table.add_row("Mode", "[yellow]AUTOMATIC[/yellow]" if status.mode == HeaterMode.AUTOMATIC else "[yellow]LEVEL[/yellow]")
            status_table.add_row("Running State", f"[green]{running_state_description}[/green]")
            status_table.add_row("Room Temperature", f"[cyan]{status.temp_room}°C[/cyan]")
            status_table.add_row("Target", f"[green]{status.target_temperature_level}{'°C' if status.mode == HeaterMode.AUTOMATIC else ' (level)'}[/green]")
            status_table.add_row("Heating Temperature", f"[red]{status.temp_heating}°C[/red]")
            status_table.add_row("Battery", f"[magenta]{status.voltage_battery:.1f}V[/magenta]")
            
            commands = """
[bold green]Available Commands:[/bold green]
[white]P0[/white] - Turn heater OFF
[white]P1[/white] - Turn heater ON
[white]T8-T36[/white] - Set temperature (8-36°C)
[white]L1-L10[/white] - Set power level (1-10)
[white]exit[/white] - Exit program

Enter command: """
            
            layout["status"].update(Panel(status_table, title="Status"))
            layout["commands"].update(Panel(commands, title="Commands"))
            
            self.console.print(layout)


    def __init__(self, mac_address: str):
        self.mac_address = mac_address
        self.peripheral: Optional[Peripheral] = None
        self.logger = logging.getLogger("VEVORHeater")
        self.console = Console()
        logging.basicConfig(level=logging.INFO)

    def connect(self):
        """Connect to BLE device"""
        try:
            self.peripheral = Peripheral(self.mac_address, "public")
            self.peripheral.setDelegate(self.NotificationDelegate(self, self.console))
            self.logger.info(f"Connected to {self.mac_address}")
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            raise

    def disconnect(self):
        """Disconnect from device"""
        if self.peripheral:
            try:
                self.peripheral.disconnect()
                self.peripheral = None
                self.logger.info("Disconnected")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")

    def calculate_checksum(self, data: bytearray) -> int:
        """Calculate checksum"""
        return sum(data[2:]) % 256

    def create_command(self, command_type: int, value: int) -> bytearray:
        """Create command with checksum"""
        data = bytearray([
            *self.HEADER,
            0x0C,  # Fixed packet length
            0x22,  # Fixed packet type
            command_type,
            value,
            0x00,  # Reserved
            0x00   # Checksum placeholder
        ])
        data[-1] = self.calculate_checksum(data)
        return data

    def send_command(self, command: bytearray):
        """Send command to BLE device and read response"""
        if not self.peripheral:
            raise ConnectionError("Device not connected")

        try:
            service = self.peripheral.getServiceByUUID(self.SERVICE_UUID)
            char = service.getCharacteristics(self.CHAR_UUID)[0]

            char.write(command, withResponse=True)

            if self.peripheral.waitForNotifications(1.0):
                self.logger.info("Notification received")

            response = char.read()
            return list(response)
        except Exception as e:
            self.logger.error(f"Error sending command: {e}")
            return None

    def set_mode(self, mode: HeaterMode):
        cmd = self.create_command(HeaterCommand.MODE, mode)
        self.send_command(cmd)

    def set_power(self, power: bool):
        value = HeaterPower.ON if power else HeaterPower.OFF
        cmd = self.create_command(HeaterCommand.POWER, value)
        self.send_command(cmd)

    def set_level(self, level: int):
        if not 0 <= level <= 10:
            raise ValueError("Level must be between 0 and 10")
        self.set_mode(HeaterMode.LEVEL)
        cmd = self.create_command(HeaterCommand.LEVEL_OR_TEMP, level)
        self.send_command(cmd)

    def set_temperature(self, temp: int):
        if not 8 <= temp <= 36:
            raise ValueError("Temperature must be between 8°C and 36°C")
        self.set_mode(HeaterMode.AUTOMATIC)
        cmd = self.create_command(HeaterCommand.LEVEL_OR_TEMP, temp)
        self.send_command(cmd)

def communication_thread(heater: VEVORHeater, stop_event: threading.Event):
    """Thread function for sending and receiving data"""
    common_bytes = bytearray([0xAA, 0x55, 0x0C, 0x22])
    cmd = common_bytes + bytearray([0x01, 0x00, 0x00, 0x2F])

    while not stop_event.is_set():
        try:
            response = heater.send_command(cmd)
        except Exception as e:
            heater.console.print(f"[red]Communication error: {e}[/red]")
        time.sleep(1)

def main():
    console = Console()
    heater = VEVORHeater("21:47:08:1a:b1:1e")
    stop_event = threading.Event()  # Initialize stop_event at the start
    
    try:
        console.print("[yellow]Connecting to heater...[/yellow]")
        heater.connect()
        console.print("[green]Connected successfully![/green]")
        
        thread = threading.Thread(target=communication_thread, args=(heater, stop_event))
        thread.start()

        while True:
            cmd = input().lower()

            if cmd == "exit":
                console.print("[yellow]Shutting down...[/yellow]")
                stop_event.set()
                break
            elif cmd in ["p0", "p1"]:
                try:
                    heater.set_power(True if cmd == "p1" else False)
                    console.print(f"[green]Power {'ON' if cmd == 'p1' else 'OFF'}[/green]")
                except Exception as e:
                    console.print(f"[red]Error setting power: {e}[/red]")
            elif cmd.startswith("t"):
                try:
                    temp = int(cmd[1:])
                    if 8 <= temp <= 36:
                        heater.set_temperature(temp)
                        console.print(f"[green]Temperature set to {temp}°C[/green]")
                    else:
                        console.print("[red]Temperature must be between 8°C and 36°C[/red]")
                except ValueError:
                    console.print("[red]Invalid temperature format[/red]")
            elif cmd.startswith("l"):
                try:
                    level = int(cmd[1:])
                    if 0 <= level <= 10:
                        heater.set_level(level)
                        console.print(f"[green]Power level set to {level}[/green]")
                    else:
                        console.print("[red]Level must be between 0 and 10[/red]")
                except ValueError:
                    console.print("[red]Invalid level format[/red]")
            else:
                console.print("[red]Invalid command[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        console.print("[yellow]Disconnecting...[/yellow]")
        stop_event.set()
        thread.join()
        heater.disconnect()
        console.print("[green]Disconnected successfully[/green]")

if __name__ == "__main__":
    main()
