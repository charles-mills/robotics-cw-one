import time

from inputs import SelectButton, CycleButton
from managers import SettingsDial, AlertManager
from outputs import Led, Fan, Lcd
from sensors import Ultrasonic, Dht


class Main:
    def __init__(self):
        self.alert_manager = AlertManager()

        self.ultrasonic = Ultrasonic(1, self.alert_manager)
        self.dht = Dht(2, self.alert_manager)
        self.led = Led(3, self.alert_manager)
        self.fan = Fan(4, self.alert_manager)

        self.settings_dial = SettingsDial()
        self.lcd = Lcd(self.alert_manager, self.dht, self.settings_dial)
        self.select_btn = SelectButton(5, self.lcd)
        self.cycle_btn = CycleButton(6, self.lcd)

        self.components = [self.ultrasonic, self.dht, self.cycle_btn, self.select_btn, self.led, self.fan, self.lcd]

    def main(self):
        self.ultrasonic.establish_baseline_distance()

        while True:
            try:
                for component in self.components:
                    component.tick()
                time.sleep(0.1)

            except IOError:
                print("IOError")
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main = Main()
    main.main()
