from inputs.base_btn import BaseButton
from outputs import Lcd


class CycleButton(BaseButton):

    def __init__(self, port: int, display: Lcd):
        super().__init__(port)
        self.display: Lcd = display

    def tick(self):
        """
        Checks the state of the button during each system loop. 
        If a new button press is detected it cycles through the different states on the LCD.
        """
        if self.was_pressed():
            self.display.cycle_states()
