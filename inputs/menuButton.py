import grovepi
from inputs.button import Button 
from outputs.lcd import Lcd

class MenuButton(Button):

    def __init__(self, port: int, display: Lcd):
        super().__init__(port) 
        self.display: Lcd = display
        self.button_last_state: int = 0

    
    def check_and_cycle_states(self) -> None:
        
        current_state: int = self.get_value()

        if current_state == 1 and self.button_last_state == 0:
            self.display.cycle_states()
        

        self.button_last_state = current_state
