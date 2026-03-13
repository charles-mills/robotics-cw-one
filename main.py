from sensors.ultrasonic import Ultrasonic
from sensors.dht import Dht
from sensors.led import Led
from sensors.fan import Fan
from sensors.button import Button
from outputs.lcd import Lcd

class Main:
    def __init__(self):
        self.ultrasonic = Ultrasonic(1)
        self.dht = Dht(2)
        self.led = Led(3)
        self.fan = Fan(4)
        self.cycleBtn = Button(5)
        self.triggerBtn = Button(6)
        self.lcd = Lcd()

    def main(self):
        pass

if __name__ == "__main__":
    main = Main()
    main.main()