import time

from inputs import MenuButton, AlarmButton
from outputs import Led, Fan, Lcd
from sensors import Ultrasonic, Dht


class Main:
    def __init__(self):
        self.ultrasonic = Ultrasonic(1)
        self.dht = Dht(2)
        self.led = Led(3)
        self.fan = Fan(4)
        self.lcd = Lcd()
        self.cycle_btn = MenuButton(5, self.lcd)
        self.trigger_btn = AlarmButton(6)

    def main(self):
        self.ultrasonic.establish_baseline_distance()

        while True:
            try:
                self.cycle_btn.check_and_cycle_states()

                self.trigger_btn.change_alarm_state()

                motion_detected = self.ultrasonic.is_detected()
                current_temp, current_humidity = self.dht.get_value()

                self.dht.temp = current_temp
                self.dht.humidity = current_humidity

                high_temp: bool = current_temp > 28
                high_humidity = current_humidity > 60

                high_climate: bool = high_temp and high_humidity

                self.led.light_state = motion_detected or high_climate

                time.sleep(0.1)
            except IOError:
                print("IOError")


if __name__ == "__main__":
    main = Main()
    main.main()
