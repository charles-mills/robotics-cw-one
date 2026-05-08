import time
from enum import Enum, auto

import RPi.GPIO as GPIO
import smbus
from managers import AlertManager, SettingsDial
from managers.alert_manager import Alert
from sensors import Dht


class LcdState(Enum):
    SETTINGS = auto()
    DASHBOARD = auto()
    ALERT = auto()


class SettingsOption(Enum):
    DASHBOARD = auto()
    OPTION2 = auto()
    OPTION3 = auto()

class Lcd:
    def __init__(self, alert_manager: AlertManager, dht: Dht) -> None:
        self.DISPLAY_RGB_ADDR: int = 0x62
        self.DISPLAY_TEXT_ADDR: int = 0x3e
        self._lcd_state: LcdState = LcdState.DASHBOARD
        self.lcd_state_timer: int = 4
        self._current_settings_option: list[SettingsOption] = list(SettingsOption)
        self._current_option_index: int = 0
        self._current_string_index: int = 0

        # TODO: this type hint should be optional / or none but again will need to see if that works on the Pi
        self._last_text: str = None

        # TODO: find out if the Python ver supports tuple hinting
        self._last_rgb = None

        self._last_select_click: float = 0.0

        self.alert_manager: AlertManager = alert_manager
        self.dht: Dht = dht

        rev = GPIO.RPI_REVISION

        if rev == 2 or rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

    def set_rgb(self, r: int, g: int, b: int) -> None:
        if self._last_rgb == (r, g, b):
            return

        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0, 0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 1, 0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0x08, 0xaa)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 4, r)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 3, g)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 2, b)
        self._last_rgb = (r, g, b)

    # Don't think these are needed for the LCD
    # def get_value(self) -> int:
    #     return grovepi.analogRead(self.port)

    # def shutdown(self) -> int:
    #     return grovepi.pinMode(self.port, "OUTPUT")

    def text_command(self, cmd: int) -> None:
        """
        Sends an instruction to the screen.

        Args:
            cmd (int): The hexadecimal command code that needs to be executed.
        
        Returns:
            None
        """
        self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR, 0x80, cmd)

    def clear_display(self) -> bool:
        self.text_command(0x01)
        self._last_text = None
        self.set_rgb(0, 0, 0)
        return True

    def text_no_refresh(self, text: str) -> None:
        """
        Writes a string to the LCD without clearing the screen
        which prevents the screen from flickering when updating.

        Args:
            text (str): The string that needs to be displayed to the screen.

        Returns:
            None
        """

        while len(text) < 32:
            text += ' '

        if self._last_text == text:
            return

        self.text_command(0x02)
        time.sleep(0.05)
        self.text_command(0x08 | 0x04)
        self.text_command(0x28)
        time.sleep(0.05)

        lines: list[str] = text.split('\n')

        if len(lines) == 1:
            lines.append("")

        line1: str = lines[0].ljust(16, ' ')[:16]
        line2: str = lines[1].ljust(16, ' ')[:16]

        new_text: str = line1 + line2

        count: int = 0

        for c in new_text:
            if count == 16:
                self.text_command(0xc0)
            
            self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR, 0x40, ord(c))
            count += 1

        self._last_text = text

    def render_dashboard(self, temp: float, humidity: float) -> None:
        """
        Formats and displays the different components in the dashboard. 

        Args:
            temp (float): The current temperature.
            humidity (float): The current humidity.

        Returns:
            None
        """

        display_string: str = f"Temp:{temp:.1f}C \n Hum:{humidity:.0f}%"
        self.text_no_refresh(display_string)

    def render_settings_option(self) -> None:
        """
        Formats the settings options where it renders a 2 scrolling settings menu.
        The currently selected option is the top row

        Returns:
            None
        """

        current_option_name: str = self.current_settings_option.name

        next_option_index: int = (self._current_option_index + 1) % len(self._current_settings_option)
        next_option_name: str = self._current_settings_option[next_option_index].name

        display_string: str = f"> {current_option_name} \n {next_option_name}"
        self.text_no_refresh(display_string)

    def render_alert_notification(self, alert: Alert) -> None:
        """
        Formats and displays the given alerts caught by the alert manager the dashboard.

        Args:
            alert (Alert): the alert to be displayed

        Returns:
            None
        """

        display_string: str = f"{alert.alert_type.name}: {alert.timestamp}\n{self.cycle_through_string(alert.message)}"
        self.text_no_refresh(display_string)

    def cycle_through_string(self, text: str, window_size: int = 12) -> str:
        text_len: int = len(text)

        if text_len <= window_size:
            return text

        self._current_string_index = (self._current_string_index + 1) % text_len
        return (text + text)[self._current_string_index:self._current_string_index + window_size]

    @property
    def lcd_state(self) -> LcdState:
        return self._lcd_state

    @lcd_state.setter
    def lcd_state(self, new_state: LcdState) -> None:
        self._lcd_state = new_state

    def cycle_states(self) -> None:
        if self._lcd_state == LcdState.DASHBOARD:
            self._lcd_state = LcdState.SETTINGS
        elif self._lcd_state == LcdState.SETTINGS:
            self.next_setting()

    def select(self) -> None:

        if self.alert_manager.total_alert > 0:
            self.alert_manager.dismiss_alert()

        elif self._lcd_state == LcdState.SETTINGS:

            if self.current_settings_option.name == "DASHBOARD":
                self.lcd_state = LcdState.DASHBOARD
            else:
                pass

    def handle_alerts_if_any(self) -> bool:
        if len(self.alert_manager.active_alerts) < 0:
            return False

        self.alert_manager.try_resolve_alerts(self.dht.temp, self.dht.humidity)
        self.render_alert_notification(self.alert_manager.current_alert)
        self.set_rgb(255, 0, 0)

        return True

    def tick(self):
        if self.handle_alerts_if_any():
            return

        # TODO: can rework this with a proper stack for menus
        match self.lcd_state:
            case LcdState.DASHBOARD:
                self.lcd_state_timer = 4
                self.render_dashboard(self.dht.temp, self.dht.humidity)
            case LcdState.SETTINGS:
                if self.lcd_state_timer > 0:
                    self.lcd_state_timer = self.lcd_state_timer - 1
                else:
                    self.lcd_state_timer =4
                    self.render_dashboard(self.dht.temp, self.dht.humidity)
            case LcdState.ALERT:
                self.lcd_state = LcdState.DASHBOARD

        self.set_rgb(54, 224, 148)

    def next_setting(self) -> None:
        self._current_option_index = (self._current_option_index + 1) % len(self._current_settings_option)

    def previous_setting(self) -> None:
        self._current_option_index = (self._current_option_index - 1) % len(self._current_settings_option)

    @property
    def current_settings_option(self) -> SettingsOption:
        return self._current_settings_option[self._current_option_index]
