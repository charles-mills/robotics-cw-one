import grovepi
from managers import AlertManager

'''

Class names = UpperCaseWhateverItsCalled
Method names = like_this
Variable names = like_this

'''


class Led:
    def __init__(self, port: int, alert_manager: AlertManager) -> None:
        self.port: int = port
        self.alert_manager: AlertManager = alert_manager
        grovepi.pinMode(self.port, "OUTPUT")
        grovepi.digitalWrite(self.port, 0)
        self._led_on: bool = False

    def tick(self):
        self.led_on = self.alert_manager.total_alert > 0

    @property
    def led_on(self) -> bool:
        return self._led_on

    @led_on.setter
    def led_on(self, value: bool) -> None:
        self._led_on = value
        grovepi.digitalWrite(self.port, 1 if value else 0)
