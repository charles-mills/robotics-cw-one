import grovepi

class Dht:
    def __init__(self, port):
        grovepi.set_bus("RPI_1")
        self.port = port
        self.type = 0
    
    def get_value(self):
        # [temp, humidity] = grovepi.dht(self.port, type)
        return grovepi.dht(self.port, self.type)
