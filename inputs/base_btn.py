import grovepi


class BaseButton:
    def __init__(self, port: int):
        self.port: int = port
        grovepi.pinMode(self.port, "INPUT")

    def get_value(self) -> int:
        return grovepi.digitalRead(self.port)

    def shutdown(self) -> int:
        return grovepi.pinMode(self.port, "OUTPUT")
