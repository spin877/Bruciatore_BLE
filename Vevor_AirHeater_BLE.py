import os
from bluepy.btle import Peripheral, DefaultDelegate
import threading
import time

from Bruciatore_BLE import Bruciatore_BLE  # Importa la classe Bruciatore_BLE dal modulo Bruciatore_ble


# Creare una sottoclasse di DefaultDelegate per gestire le notifiche
class MyDelegate(DefaultDelegate):
    def handleNotification(self, cHandle, data):
        # Questo metodo verrà chiamato quando una notifica è ricevuta
        bruciatore = Bruciatore_BLE(list(data))
        bruciatore.dump()


# Indirizzo del dispositivo BLE a cui desideri connetterti
target_address = "21:47:08:1a:b1:1e"

# Servizio e caratteristica di interesse
service_uuid = "0000ffe0-0000-1000-8000-00805f9b34fb"
characteristic_uuid = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Definisci i comandi
common_bytes = bytearray([0xaa, 0x55, 0x0c, 0x22])

cmd1  = common_bytes + bytearray([0x01, 0x00, 0x00, 0x2f])

cmd2  = common_bytes + bytearray([0x04, 0xa0, 0x00, 0x3c])

#cmd3  = common_bytes + bytearray([0x02, 0x02, 0x00, 0x32]) # lampeggia temeratura target per regolarla #36 gradi
#cmd4  = common_bytes + bytearray([0x04, 0x24, 0x00, 0x56]) # lampeggia 8 gradi

cmd5  = common_bytes + bytearray([0x02, 0x01, 0x00, 0x31]) # Manual Mode Level
cmd6  = common_bytes + bytearray([0x02, 0x02, 0x00, 0x32]) # Automatic Mode

cmd8  = common_bytes + bytearray([0x03, 0x00, 0x00, 0x31]) # OFF
cmd10 = common_bytes + bytearray([0x03, 0x01, 0x00, 0x32]) # ON

cmd11 = common_bytes + bytearray([0x04, 0x01, 0x00, 0x33])  #1
cmd12 = common_bytes + bytearray([0x04, 0x02, 0x00, 0x34])  #2
cmd13 = common_bytes + bytearray([0x04, 0x03, 0x00, 0x35])  #3
cmd14 = common_bytes + bytearray([0x04, 0x04, 0x00, 0x36])  #4
cmd15 = common_bytes + bytearray([0x04, 0x05, 0x00, 0x37])  #5
cmd16 = common_bytes + bytearray([0x04, 0x06, 0x00, 0x38])  #6
cmd17 = common_bytes + bytearray([0x04, 0x07, 0x00, 0x39])  #7
cmd18 = common_bytes + bytearray([0x04, 0x08, 0x00, 0x3a])  #8
cmd19 = common_bytes + bytearray([0x04, 0x09, 0x00, 0x3b])  #9

def auto_command_thread():
    while True:
        # Invia automaticamente il comando cmd1
        response = characteristic.write(cmd1, withResponse=True)

        data = characteristic.read()

        time.sleep(1)  # Attendere 2 secondi prima di inviare il comando successivo
        print("\r\ni comandi supportati sono cmd1-19\r\n")

try:
    # Connessione al dispositivo BLE
    peripheral = Peripheral(target_address, "public")

    # Trova il servizio desiderato
    service = peripheral.getServiceByUUID(service_uuid)

    if service is not None:
        # Trova la caratteristica desiderata
        characteristic = service.getCharacteristics(characteristic_uuid)[0]

        if characteristic is not None:
            peripheral.setDelegate(MyDelegate())
            
            # Creare e avviare il thread per l'invio automatico del comando
            auto_thread = threading.Thread(target=auto_command_thread)
            auto_thread.daemon = True  # Il thread si esce quando il programma principale termina
            auto_thread.start()

            while True:
                command = input("Inserisci un comando (o 'exit' per uscire): ").strip()
                if command.lower() in ['exit', 'close', 'quit', 'q']:
                    break
                elif command.startswith('cmd'):
                    # Ottieni il numero del comando
                    cmd_num = int(command[3:])
                    if cmd_num >= 1 and cmd_num <= 21:
                        # Ottieni il comando corrispondente
                        cmd = eval(f'cmd{cmd_num}')
                        # Invia il comando come richiesta
                        response = characteristic.write(cmd, withResponse=True)

                    else:
                        print("Comando non valido. Inserisci un comando da 'cmd1' a 'cmd19'.")
                else:
                    print("Comando non valido. Inserisci un comando da 'cmd1' a 'cmd19' o 'exit'.")
        else:
            print(f"Caratteristica con UUID {characteristic_uuid} non trovata.")
    else:
        print(f"Servizio con UUID {service_uuid} non trovato.")

    # Disconnettiti dal dispositivo BLE
    peripheral.disconnect()

except Exception as e:
    print(f"Errore durante la connessione o la lettura dei dati: {str(e)}")
