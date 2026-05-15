import grovepi
from managers import AlertManager

class Led:
    def __init__(self, port: int, alert_manager: AlertManager) -> None:
        self.port: int = port
        self.alert_manager: AlertManager = alert_manager
        grovepi.pinMode(self.port, "OUTPUT")
        grovepi.digitalWrite(self.port, 0)
        self._led_on: bool = False

    def tick(self):
        """
        Periodically checks the system state to update the LED.
        If there are 1 or more active alerts the LED turns on, otherwise it stays off.
        """
        self.led_on = self.alert_manager.total_alert > 0

    @property
    def led_on(self) -> bool:
        """
        Gets the current state of the LED.

        Returns:
            bool: Returns True if the LED is currently on, False otherwise.
        """
        return self._led_on

    @led_on.setter
    def led_on(self, value: bool) -> None:
        """
        Sets the state of the LED and updates the internal tracker.

        Args:
            value (bool): True to turn the LED on and False to turn it off.
        """
        self._led_on = value
        grovepi.digitalWrite(self.port, 1 if value else 0)
