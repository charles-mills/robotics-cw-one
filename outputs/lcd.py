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
    OPTION1 = auto()
    OPTION2 = auto()
    OPTION3 = auto()


class Lcd:
    def __init__(self, alert_manager: AlertManager, dht: Dht, settings_dial: SettingsDial) -> None:
        self.DISPLAY_RGB_ADDR: int = 0x62
        self.DISPLAY_TEXT_ADDR: int = 0x3e
        self._lcd_state: LcdState = LcdState.DASHBOARD
        self.lcd_state_timer: int = 4
        self._current_settings_option: list[SettingsOption] = list(SettingsOption)
        self._current_option_index: int = 0
        self._current_string_index: int = 0

        self.alert_manager: AlertManager = alert_manager
        self.dht: Dht = dht
        self.settings_dial: SettingsDial = settings_dial

        rev = GPIO.RPI_REVISION

        if rev == 2 or rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

    def set_rgb(self, r: int, g: int, b: int) -> None:
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0, 0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 1, 0)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 0x08, 0xaa)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 4, r)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 3, g)
        self.bus.write_byte_data(self.DISPLAY_RGB_ADDR, 2, b)

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

        self.text_command(0x02)
        time.sleep(0.05)
        self.text_command(0x08 | 0x04)
        self.text_command(0x28)
        time.sleep(0.05)

        count: int = 0
        row: int = 0

        while len(text) < 32:
            text += ' '

        for c in text:
            if c == '\n' or count == 16:
                count = 0

                row += 1

                if row == 2:
                    break

                self.text_command(0xc0)

                if c == '\n':
                    continue

            count += 1
            self.bus.write_byte_data(self.DISPLAY_TEXT_ADDR, 0x40, ord(c))

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

        # Find nice colour again
        self.set_rgb(0, 0, 255)

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

        self.set_rgb(255, 0, 0)

        display_string: str = f"{alert.alert_type.name}: {alert.timestamp}\n{self.cycle_through_string(alert.message)}"
        self.text_no_refresh(display_string)

    def cycle_through_string(self, text: str, window_size: int = 12) -> str:
        text_len: int = len(str)

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
            self._lcd_state = LcdState.DASHBOARD

    def select(self) -> None:

        if self.alert_manager.total_alert > 0:
            self.alert_manager.dismiss_alert()
        elif self._lcd_state == LcdState.SETTINGS:
            pass

    def tick(self):
        if len(self.alert_manager.active_alerts) == 0:
            if self.lcd_state == LcdState.DASHBOARD:
                self.lcd_state_timer = 4
                # Should we be using parameters here? It's all internal
                self.render_dashboard(self.dht.temp, self.dht.humidity)

            elif self.lcd_state == LcdState.SETTINGS:
                if self.lcd_state_timer > 0:
                    self.lcd_state_timer = self.lcd_state_timer - 1
                else:
                    self.lcd_state_timer = 4
                    rotation_value: int = self.settings_dial.get_rotation()

                    if rotation_value == 1:
                        self.next_setting()
                    elif rotation_value == -1:
                        self.previous_setting()

                    self.render_settings_option()

            elif self.lcd_state == LcdState.ALERT:
                self.lcd_state = LcdState.DASHBOARD
        else:
            self.alert_manager.try_resolve_alerts(self.dht._temp, self.dht._humidity)
            self.render_alert_notification(self.alert_manager.current_alert)

    def next_setting(self) -> None:
        self._current_option_index = (self._current_option_index + 1) % len(self._current_settings_option)

    def previous_setting(self) -> None:
        self._current_option_index = (self._current_option_index - 1) % len(self._current_settings_option)

    @property
    def current_settings_option(self) -> SettingsOption:
        return self._current_settings_option[self._current_option_index]
