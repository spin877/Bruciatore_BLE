class Bruciatore_BLE:
    def __init__(self, byte_sequence):
        self.byte_sequence = byte_sequence

    def get_accensione(self):
        return bool(self.byte_sequence[3] )

    def get_accensione_candelette(self):
        if self.byte_sequence[5] == 0:
            return 'Spenta'
        if self.byte_sequence[5] == 2:
            return 'Iniezione'
        if self.byte_sequence[5] == 3:
            return 'Riscaldamento'
        if self.byte_sequence[5] == 4:
            return 'Spegnimento'

    def get_potenza(self):
        return self.byte_sequence[9]

    def get_temperatura(self):
        return self.byte_sequence[15]

    def get_temperatura_uscita_bruciatore(self):
        return self.byte_sequence[13]

    def get_temperatura_bruciatore(self):        
        if self.byte_sequence[13] > 150 and self.byte_sequence[19] < 50:
           return self.byte_sequence[19] + 255
        else:
          return self.byte_sequence[19]

    def get_velocita_ventola(self):
        return self.byte_sequence[10] + 1

    def get_Volt_battery(self):
        return self.byte_sequence[11] / 10.0

    def get_Altitudine(self):
        return self.byte_sequence[6]

    def get_modolaita_operativa(self):
        if self.byte_sequence[8] == 1:
            return('Manuale')
        else:
            return('Automatico')
    
    def get_ErrorCode(self):
        return self.byte_sequence[17]

    def dump(self):
                print(f"Accensione: {'Acceso' if self.get_accensione() else 'Spento'}")
                print(f"Modalità operativa: {self.get_modolaita_operativa()}")
                print(f"Potenza: {self.get_potenza()}")
                print(f"Temperatura: {self.get_temperatura()}°C")
                print(f"Temperatura interna Bruciatore: {self.get_temperatura_bruciatore()}°C")
                print(f"Temperatura Uscita Bruciatore: {self.get_temperatura_uscita_bruciatore()}°C")
                print(f"Velocità ventola", self.get_velocita_ventola())
                print(f"Candeletta Modalita: {self.get_accensione_candelette()}")
                print(f"Volt Batteria: {self.get_Volt_battery()} Volt")
                print(f"Decimal representation: {[x for x in self.byte_sequence]}")
                print(f"Hex representation: {[hex(x) for x in self.byte_sequence]}")
                print(f"Altitudine: {self.get_Altitudine()}")
                print(f"Error Code: {self.get_ErrorCode()}")
                print(f"i comandi supportati sono cmd1-19\r\n")
