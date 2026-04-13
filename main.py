from sensors import Ultrasonic, Dht
from inputs import Button
from outputs import Led, Fan, Lcd


class Main:
    def __init__(self):
        self.ultrasonic = Ultrasonic(1)
        self.dht = Dht(2)
        self.led = Led(3)
        self.fan = Fan(4)
        self.cycle_btn = Button(5)
        self.trigger_btn = Button(6)
        self.lcd = Lcd()

    def main(self):
        pass


if __name__ == "__main__":
    main = Main()
    main.main()
