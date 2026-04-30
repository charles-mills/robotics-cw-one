import grovepi
from managers import AlertManager, AlertType


class Fan:
    def __init__(self, port: int, alert_manager: AlertManager):
        self.port: int = port
        self.alert_manager: AlertManager = alert_manager
        self.power: int = 0
        grovepi.pinMode(self.port, "OUTPUT")

    def tick(self):
        if self.alert_manager.has_alert_type(AlertType.HIGH_TEMP):
            self.set_value(255)
        else:
            self.set_value(0)

    def set_value(self, new_power: int) -> None:
        grovepi.analogWrite(self.port, new_power)
        self.power = new_power
