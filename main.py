from sensors import Ultrasonic, Dht
from inputs import BaseButton
from outputs import Led, Fan, Lcd


class Main:
    def __init__(self):
        self.ultrasonic = Ultrasonic(1)
        self.dht = Dht(2)
        self.led = Led(3)
        self.fan = Fan(4)
        self.cycle_btn = BaseButton(5)
        self.trigger_btn = BaseButton(6)
        self.lcd = Lcd()

    def main(self):
        pass


if __name__ == "__main__":
    main = Main()
    main.main()
