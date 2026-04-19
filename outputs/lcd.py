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