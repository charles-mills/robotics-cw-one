import time

from enum import Enum, auto

import RPi.GPIO as GPIO
import grovepi
import smbus


class LcdState(Enum):
    SETTINGS = auto()
    DASHBOARD = auto()

class SettingsOption(Enum):
    OPTION1 = auto()
    OPTION2 = auto()
    OPTION3 = auto()

class Lcd:
    def __init__(self) -> None:
        self.rgbAddr: int = 0x62
        self.txtAddr: int = 0x3e
        self._lcd_state: LcdState = LcdState.DASHBOARD
        self._current_settings_option: list[SettingsOption] = list(SettingsOption)
        self._current_option_index: int = 0

        rev = GPIO.RPI_REVISION

        if rev == 2 or rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

    def set_rgb(self, r: int, g: int, b: int) -> None:
        self.bus.write_byte_data(self.rgbAddr, 0, 0)
        self.bus.write_byte_data(self.rgbAddr, 1, 0)
        self.bus.write_byte_data(self.rgbAddr, 0x08, 0xaa)
        self.bus.write_byte_data(self.rgbAddr, 4, r)
        self.bus.write_byte_data(self.rgbAddr, 3, g)
        self.bus.write_byte_data(self.rgbAddr, 2, b)

    # Dont think these are needed for the LCD
    # def get_value(self) -> int:
    #     return grovepi.analogRead(self.port)

    # def shutdown(self) -> int:
    #     return grovepi.pinMode(self.port, "OUTPUT")

    def text_command(self, cmd: int) -> None:
        """
        Sends a instruction to the screen.

        Args:
            cmd (int): The hexadecimal command code that needs to be executed.
        
        Returns:
            None
        """
        self.bus.write_byte_data(self.txtADDR, 0x80, cmd)

    def text_norefresh(self, text: str) -> None:
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
            self.bus.write_byte_data(self.txtAddr, 0x40, ord(c))


    def render_dashboard(self, temp: float, humidity: float, alerts: int) -> None:
        """
        Formats and displays the different components in the dashboard. 

        Args:
            temp (float): The current temperature.
            humidity (float): The current humidity.
            alerts (int): The number of active alerts.
        """
        
        if alerts == 0:
            status_text: str = "No alerts"
            self.set_rgb(0, 255, 0)
        else:
            status_text: str = f"Alerts: {alerts}"
            self.set_rgb(255, 0, 0)

        display_string: str = f"{status_text} \n Temp:{temp:.1f}C Hum:{humidity:.0f}%"
        self.text_norefresh(display_string)



    


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


    def next_setting(self) -> None:
        self._current_option_index = (self._current_option_index + 1) % len(self._current_settings_option)

    
    def previous_setting(self) -> None:
        self._current_option_index = (self._current_option_index - 1) % len(self._current_settings_option)

    
    @property
    def current_settings_option(self) -> SettingsOption:
        return self._current_settings_option[self._current_option_index]