import grovepi


class Fan:
    def __init__(self, port: int):
        self.port: int = port
        self.power: int = 0
        grovepi.pinMode(self.port, self.power)

    def set_value(self, new_power: int) -> None:
        grovepi.analogWrite(self.port, new_power)
        self.power = new_power

    def get_value(self) -> int:
        return grovepi.analogRead(self.port)

    def shutdown(self) -> int:
        return grovepi.pinMode(self.port, "OUTPUT")
