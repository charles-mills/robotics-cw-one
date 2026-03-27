import grovepi

class Dht:
    def __init__(self, port: int):
        grovepi.set_bus("RPI_1")
        self.port: int = port
        self.type: int = 0
        self.temp: float = 0
        self.humidity: float = 0
    
    def get_value(self) -> tuple[float, float] :
        # [temp, humidity] = grovepi.dht(self.port, type)
        return grovepi.dht(self.port, self.type)
    

    def set_temp(self, newTempValue : float) -> None:
        self.temp = newTempValue


    def get_temp(self) -> float:
        return self.temp
    
    
    def set_humidity(self, newHumidityValue : float) -> None:
        self.humidity = newHumidityValue

    
    def get_humidity(self) -> float:
        return self.humidity