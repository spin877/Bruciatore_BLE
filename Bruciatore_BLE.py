class Bruciatore_BLE:
    def __init__(self, byte_sequence):
        self.byte_sequence = byte_sequence

    def get_accensione(self):
        return bool(self.byte_sequence[3] )
  
    def get_accensione_candelette(self):
        if self.byte_sequence[5] == 0:            
            return 'Spenta'
        if self.byte_sequence[5] == 2:            
            return 'Accesa'
        if self.byte_sequence[5] == 3:            
            return 'Stambay mode'
        if self.byte_sequence[5] == 4:            
            return 'Spegnimento'
        
    def get_potenza(self):
        return self.byte_sequence[10] +1

    def get_temperatura(self):
        return self.byte_sequence[15] 

    def get_temperatura_uscita_bruciatore(self):
        return self.byte_sequence[13] # 

    def get_temperatura_bruciatore(self):
        return self.byte_sequence[19] # 

    def get_temperatura_target(self):
        return self.byte_sequence[9] # non è una temperatura sembra seguire la potenza
    
    def get_Volt_battery(self):    
        return self.byte_sequence[11] / 10.0
    
    def get_Altitudine(self):
        return self.byte_sequence[6]

    def dump(self):
                                                                                                   
                print(f"Accensione: {'Acceso' if self.get_accensione() else 'Spento'}")
                print(f"Potenza: {self.get_potenza()}")
                print(f"Temperatura: {self.get_temperatura()}°C")
                print(f"Temperatura interna Bruciatore: {self.get_temperatura_bruciatore()}°C")
                print(f"Temperatura Uscita Bruciatore: {self.get_temperatura_uscita_bruciatore()}°C")
                print(f"Temperatura Target: {self.get_temperatura_target()}°C")
                print(f"Candeletta Modalita: {self.get_accensione_candelette()}")
                print(f"Volt Batteria: {self.get_Volt_battery()} Volt")
                print(f"Decimal representation: {[x for x in self.byte_sequence]}")
                print(f"Altitudine: {self.get_Altitudine()}")
                print(f"i comandi supportati sono cmd1-19\r\n")