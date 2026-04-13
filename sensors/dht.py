import grovepi

class Dht:
    def __init__(self, port: int):
        grovepi.set_bus("RPI_1")
        self.port: int = port
        self.type: int = 0
        self._temp: float = 0
        self._humidity: float = 0
    
    def get_value(self) -> tuple[float, float] :
        # [temp, humidity] = grovepi.dht(self.port, type)
        return grovepi.dht(self.port, self.type)

    @property
    def temp(self) -> float:
        return self._temp

    @property
    def humidity(self) -> float:
        return self._humidity

    @temp.setter
    def temp(self, value: float) -> None:
        self._temp = value

    @humidity.setter
    def humidity(self, value: float) -> None:
        self._humidity = value