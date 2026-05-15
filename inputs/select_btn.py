import time
from inputs.base_btn import BaseButton
from outputs import LcdState
from outputs.lcd import Lcd


class SelectButton(BaseButton):

    DOUBLE_CLICK_WINDOW = 0.35

    def __init__(self, port: int, display: Lcd):
        super().__init__(port)
        self.display: Lcd = display
        self._pending_click_at: float = 0.0

    def tick(self):
        """
        Checks the state of teh button and processes its click events.
        If an alert is active or if the screen is not in the Settings menu, it executes a single 
        click. However, if in the Settings menu it queues the click and waits to see if the user has 
        single clicked in which it selects the option or double clicked to cycle through menus.
        """
        now = time.monotonic()

        if self.was_pressed():
            should_check_double_click = (self.display.lcd_state == LcdState.SETTINGS and self.display.alert_manager.total_alert == 0)

            if not should_check_double_click:
                self.display.select()
                return

            if (self._pending_click_at and now - self._pending_click_at <= self.DOUBLE_CLICK_WINDOW):
                self._pending_click_at = 0.0
                self.display.cycle_states()
                return

            self._pending_click_at = now

        if (self._pending_click_at and now - self._pending_click_at > self.DOUBLE_CLICK_WINDOW):
            self._pending_click_at = 0.0
            self.display.select()
