import grovepi
from managers import AlertManager, AlertType


class Fan:
    def __init__(self, port: int, alert_manager: AlertManager):
        self.port: int = port
        self.alert_manager: AlertManager = alert_manager
        self.power: int = 0
        grovepi.pinMode(self.port, "OUTPUT")

    def tick(self):
        """
        Periodically checks the system state to control the fan. 
        If a HIGH_TEMP alert is currently active in the AlertManager it turns the fan on at full power.
        Otherwise, it ensures the fan is turned off.
        """

        if self.alert_manager.has_alert_type(AlertType.HIGH_TEMP):
            self.set_value(255)
        else:
            self.set_value(0)

    def set_value(self, new_power: int) -> None:
        """
        Sets the power level of the fan and update the state tracker.

        Args:
            new_power (int): The analog PWM value to write to the fan.
        """
        grovepi.analogWrite(self.port, new_power)
        self.power = new_power
