import grovepi
from inputs.button import Button

class AlarmButton(Button):

    def __init__(self, port: int):
        super().__init__(port)
        self.is_alarm_on: bool = False
        self.button_last_state: int = 0

    def change_alarm_state(self) -> None:

        """
        Establishes a connection between a button press and the alarm being turend on or off.

        Returns:
            None
        
        """

        current_state: int = self.get_value()

        if current_state == 1 and self.button_last_state == 0:
            self.is_alarm_on = not self.is_alarm_on

        self.button_last_state = current_state

    @property
    def alarm_state(self) -> bool:
        
        """
        Returns the current state of the alarm.

        Returns:
            bool

        """
        
        return self.is_alarm_on