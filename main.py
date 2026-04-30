import threading
import time
import traceback

from inputs import SelectButton, CycleButton
from managers import SettingsDial, AlertManager
from outputs import Led, Fan, Lcd, Buzzer
from sensors import Ultrasonic, Dht


class Main:
    def __init__(self):
        self.alert_manager = AlertManager()

        self.ultrasonic = Ultrasonic(2, self.alert_manager)
        self.dht = Dht(3, self.alert_manager)
        self.led = Led(4, self.alert_manager)
        self.fan = Fan(5, self.alert_manager)

        self.settings_dial = SettingsDial()
        self.lcd = Lcd(self.alert_manager, self.dht, self.settings_dial)
        self.select_btn = SelectButton(6, self.lcd)
        self.cycle_btn = CycleButton(7, self.lcd)
        self.buzzer = Buzzer(8, self.alert_manager)

        self.input_components = [self.cycle_btn, self.select_btn]
        self.sensor_components = [self.ultrasonic, self.dht]
        self.output_components = [self.led, self.lcd, self.fan, self.buzzer]

        self.components = self.input_components + self.sensor_components + self.output_components
        self.threads = []

        self.threads.append(threading.Thread(target=self.input_ticks(), kwargs={"delay": 2}))
        self.threads.append(threading.Thread(target=self.sensor_ticks(), kwargs={"delay": 2}))
        self.threads.append(threading.Thread(target=self.output_ticks(), kwargs={"delay": 2}))

    def main(self):
        self.ultrasonic.establish_baseline_distance()

        while True:
            try:
                for t in self.threads:
                    t.start()

                if self.alert_manager.total_alert != 0:
                    self.lcd.set_rgb(255, 0, 0)
                else:
                    self.lcd.set_rgb(0, 255, 0)

                for t in self.threads:
                    t.join()
            except IOError:
                self.lcd.clear_display()
                traceback.print_exc()
            except KeyboardInterrupt:
                self.lcd.clear_display()
                pass

    def input_ticks(self) -> bool:
        for comp in self.input_components:
            comp.tick()

        return True

    def output_ticks(self) -> bool:
        for comp in self.output_components:
            comp.tick()

        return True

    def sensor_ticks(self) -> bool:
        for comp in self.sensor_components:
            comp.tick()

        return True


if __name__ == "__main__":
    main = Main()
    main.main()
