from inputs.base_btn import BaseButton
from outputs.lcd import Lcd


class MenuButton(BaseButton):

    def __init__(self, port: int, display: Lcd):
        super().__init__(port)
        self.display: Lcd = display
        self.button_last_state: int = 0

    def check_and_cycle_states(self) -> None:
        """
        Establishes a connection between a button press and changing the lcd states (e.g. off, dashboard, settings)

        Returns:
            None
    
        """

        current_state: int = self.get_value()

        if current_state == 1 and self.button_last_state == 0:
            self.display.cycle_states()

        self.button_last_state = current_state
