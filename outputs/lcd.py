import grovepi
import smbus
import RPi.GPIO as GPIO

class Lcd:
    def __init__(self) -> None:
        self.rgbAddr = 0x62
        self.txtAddr = 0x3e

        rev = GPIO.RPI_REVISION
        print(f"DEBUG: {rev}")
        
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

    def get_value(self) -> int:
        return grovepi.analogRead(self.port)
    
    def shutdown(self) -> int:
        return grovepi.pinMode(self.port, "OUTPUT")