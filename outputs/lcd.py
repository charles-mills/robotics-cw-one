import smbus
import RPi.GPIO as GPIO


class Lcd:
    def __init__(self):
        self.rgbAddr = 0x62
        self.txtAddr = 0x3e

        rev = GPIO.RPI_REVISION
        print(f"DEBUG: {rev}")
        
        if rev == 2 or rev == 3:
            self.bus = smbus.SMBus(1)
        else:
            self.bus = smbus.SMBus(0)

    def set_rgb(self, r, g, b):
        bus.write_byte_data(self.rgbAddr, 0, 0)
        bus.write_byte_data(self.rgbAddr, 1, 0)
        bus.write_byte_data(self.rgbAddr, 0x08, 0xaa)
        bus.write_byte_data(self.rgbAddr, 4, r)
        bus.write_byte_data(self.rgbAddr, 3, g)
        bus.write_byte_data(self.rgbAddr, 2, b)

    
    def set_rgb(self, new_power):
        grovepi.analogWrite(self.port, new_power)
        self.power = new_power

    def get_value(self):
        return grovepi.analogRead(self.port)
    
    def shutdown(self):
        grovepi.pinMode(self.port, "OUTPUT")