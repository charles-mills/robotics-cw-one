import grovepi


class BaseButton:
    def __init__(self, port: int):
        self.port: int = port
        self._last_state: int = 0
        grovepi.pinMode(self.port, "INPUT")

    def get_value(self) -> int:
        return grovepi.digitalRead(self.port)

    def was_pressed(self) -> bool:
        current_state: int = self.get_value()
        pressed: bool = current_state == 1 and self._last_state == 0
        self._last_state = current_state
        return pressed

    def shutdown(self) -> int:
        return grovepi.pinMode(self.port, "OUTPUT")
