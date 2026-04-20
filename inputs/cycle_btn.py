from inputs.base_btn import BaseButton
from outputs import Lcd

class CycleButton(BaseButton):

    def __init__(self, port: int, display: Lcd):
        super().__init__(port)
        self.display: Lcd = display

    def tick(self):
        if self.was_pressed():
            self.display.cycle_states()