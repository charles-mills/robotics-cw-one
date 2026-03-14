import grovepi

class Dht:
    def __init__(self, port: int):
        grovepi.set_bus("RPI_1")
        self.port: int = port
        self.type: int = 0
    
    def get_value(self) -> tuple[float, float] :
        # [temp, humidity] = grovepi.dht(self.port, type)
        return grovepi.dht(self.port, self.type)
