import time
from enum import Enum, auto

import RPi.GPIO as GPIO
import smbus
from managers import AlertManager
from managers.alert_manager import Alert
from sensors import Dht, Ultrasonic


class LcdState(Enum):
    SETTINGS = auto()
    DASHBOARD = auto()
    ALERT = auto()


class SettingsOption(Enum):
    RECONFIGURE_ULTRASONIC = auto()
    TOGGLE_ULTRASONIC = auto()
    DASHBOARD = auto()


class Lcd:
    def __init__(self, alert_manager: AlertManager, dht: Dht, ultrasonic: Ultrasonic) -> None:
        self.DISPLAY_RGB_ADDR: int = 0x62
        self.DISPLAY_TEXT_ADDR: int = 0x3e
        self._lcd_state: LcdState = LcdState.DASHBOARD
        self.lcd_state_timer: int = 4
        self._current_settings_option: list[SettingsOption] = list(SettingsOption)
        self._current_option_index: int = 0
        self._current_string_index: int = 0
        self._last_text: str = None
        self._last_rgb = None
        self._last_select_click: float = 0.0
        self.alert_manager: AlertManager = alert_manager
        self.dht: Dht = dht
        self.ultrasonic: Ultrasonic = ultrasonic

        rev = GPIO.RPI_REVISION

        if rev == 2 or rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

    def set_rgb(self, r: int, g: int, b: int) -> None:
        """
        Sets the RGB backlight colour of the LCD. It also prevents redundand I2C writes if the requested colour matches 
        the current colour.

        Args:
            r (int): Red value
            g (int): Green value
            b (int): Blue value
        """
        if self._last_rgb == (r, g, b):
            return

        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0, 0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 1, 0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0x08, 0xaa)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 4, r)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 3, g)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 2, b)
        self._last_rgb = (r, g, b)



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
        """
        Clears all text from the LCD display and turns the backlight off.

        Returns:
            bool: True if the clearing of screen was successful.
        """
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

    def _settings_label(self, option: SettingsOption) -> str:
        """
        Converts the SettignsOption enum into a string to display the setting options.

        Args:
            option (SettingsOption): Settings enum to display on the screen.

        Returns:
            str: Formatted string to display.
        """
        if option == SettingsOption.RECONFIGURE_ULTRASONIC:
            return "Reconfigure ultrasonic"
        if option == SettingsOption.TOGGLE_ULTRASONIC:
            return "Disable ultrasonic" if self.ultrasonic.enabled else "Enable ultrasonic"

        return "Dashboard"

    def render_settings_option(self) -> None:
        """
        Formats the settings options where it renders a 2 scrolling settings menu.
        The currently selected option is the top row

        Returns:
            None
        """

        current_option: str = self._settings_label(self.current_settings_option)
        next_option_index: int = (self._current_option_index + 1) % len(self._current_settings_option)
        next_option: str = self._settings_label(self._current_settings_option[next_option_index])

        display_string: str = f"> {current_option} \n {next_option}"
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
        """
        Creates a scrolling text by slicing based on the current index. This is used to display messages that are too
        long to fit on the screen.

        Args:
            text (str): The message that will scroll.
            window_size (int, optional): How many characters can fit on the screen. Defaults to 12.

        Returns:
            str: The substring representing the current visible frame of the scrolling text.
        """
        text_len: int = len(text)

        if text_len <= window_size:
            return text

        self._current_string_index = (self._current_string_index + 1) % text_len
        return (text + text)[self._current_string_index:self._current_string_index + window_size]

    @property
    def lcd_state(self) -> LcdState:
        """
        Gets the current UI state of the LCD.

        Returns:
            LcdState: Returns the state of the LCD.
        """
        return self._lcd_state

    @lcd_state.setter
    def lcd_state(self, new_state: LcdState) -> None:
        """
        Updates the UI state of the UI.

        Args:
            new_state (LcdState): The next state of the LCD.
        """
        self._lcd_state = new_state

    def cycle_states(self) -> None:
        """
        Handles the logic for cycling between states.
        If the state is on Dashboard then it opens Settings menu and 
        if its Settings, it scrolls down to the next option.
        """

        if self._lcd_state == LcdState.DASHBOARD:
            self._current_option_index = 0
            self._lcd_state = LcdState.SETTINGS
        elif self._lcd_state == LcdState.SETTINGS:
            self.next_setting()

    def select(self) -> None:
        """
        Handles the logic for the select button. It dimisses active alerts or 
        selects the currently selected setting option.
        """

        if self.alert_manager.total_alert > 0:
            self.alert_manager.dismiss_alert()
            return

        if self._lcd_state != LcdState.SETTINGS:
            return

        option = self.current_settings_option

        if option == SettingsOption.RECONFIGURE_ULTRASONIC:
            self.text_no_refresh("Reconfiguring...\nKeep clear from sensor")
            self.ultrasonic.reconfigure()
            self.lcd_state = LcdState.DASHBOARD
        elif option == SettingsOption.TOGGLE_ULTRASONIC:
            self.ultrasonic.toggle_enabled()
            self.render_settings_option()
        elif option == SettingsOption.DASHBOARD:
            self.lcd_state = LcdState.DASHBOARD

    def tick(self):
        """
        The main loop for LCD. It contains logic for alerts, manages UI timers, screen transitions and
        sets the display text along with background colour.
        """

        if len(self.alert_manager.active_alerts) == 0:
            if self.lcd_state == LcdState.DASHBOARD:
                self.lcd_state_timer = 4
                self.render_dashboard(self.dht.temp, self.dht.humidity)

            elif self.lcd_state == LcdState.SETTINGS:
                self.render_settings_option()
                if self.lcd_state_timer > 0:
                    self.lcd_state_timer = self.lcd_state_timer - 1
                else:
                    self.lcd_state_timer = 4
                    self.render_settings_option()

            elif self.lcd_state == LcdState.ALERT:
                self.lcd_state = LcdState.DASHBOARD
        else:
            self.alert_manager.try_resolve_alerts(self.dht.temp, self.dht.humidity)
            self.render_alert_notification(self.alert_manager.current_alert)

        if self.alert_manager.total_alert != 0:
            self.set_rgb(255, 0, 0)
        else:
            self.set_rgb(54, 224, 148)

    def next_setting(self) -> None:
        """
        Moves the settings menu cursor to the next option and it loops back 
        to the top if it reaches the end.
        """
        self._current_option_index = (self._current_option_index + 1) % len(self._current_settings_option)

    def previous_setting(self) -> None:
        """
        Moves the settings menu cursor to the previous optio where it loops to the bottom if it goes
        past the first option. 
        """
        self._current_option_index = (self._current_option_index - 1) % len(self._current_settings_option)

    @property
    def current_settings_option(self) -> SettingsOption:
        """
        Gets the SettingsOption Enum that is currently selected.

        Returns:
            SettingsOption: The active menu selection.
        """
        return self._current_settings_option[self._current_option_index]
