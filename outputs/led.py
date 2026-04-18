import grovepi

'''

Class names = UpperCaseWhateverItsCalled
Method names = like_this
Variable names = like_this

'''


class Led:
    def __init__(self, port: int) -> None:
        self.port: int = port
        grovepi.pinMode(self.port, "OUTPUT")
        grovepi.digitalWrite(self.port, 0)
        self._led_on: bool = False

    @property
    def led_on(self) -> bool:
        return self._led_on

    @led_on.setter
    def led_on(self, value: bool) -> None:
        self._led_on = value
        grovepi.digitalWrite(self.port, 1 if value else 0)
