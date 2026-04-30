import config
import grovepi

from managers import AlertManager

class Buzzer:

    def __init__(self, port, alert_manager: AlertManager) -> None:
        self.port = port
        self.alert_manager: AlertManager = alert_manager


        grovepi.pinMode(self.port, "OUTPUT")


    @property
    def sound_state(self) -> bool:
        """

        Returns True if the buzzer is making noise.

        Returns:
            bool: if the buzzer is on then it returns true otherwise, false.
        """
        return grovepi.digitalRead(self.port) == 1


    @sound_state.setter
    def sound_state(self, is_on: bool) -> None:
        """

        Turns the buzzer on or off.

        Args:
            is_on (bool): bool value indicating if the buzzer should be on or off.
        
        Returns:
            None
        """

        if not config.ALARM_SOUNDS or not is_on:
            grovepi.digitalWrite(self.port, 0)
        else:
            grovepi.digitalWrite(self.port, 1)

    
    def tick(self):
        self.sound_state = self.alert_manager.total_alert > 0
