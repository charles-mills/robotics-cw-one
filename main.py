import time

from outputs import Led, Fan, Lcd, LcdState
from inputs import SelectButton, CycleButton
from managers import SettingsDial, AlertManager, AlertType
from sensors import Ultrasonic, Dht


class Main:
    def __init__(self):
        self.ultrasonic = Ultrasonic(1)
        self.dht = Dht(2)
        self.led = Led(3)
        self.fan = Fan(4)
        self.lcd = Lcd()
        self.select_btn = SelectButton(5, self.lcd)
        self.cycle_btn = CycleButton(6, self.lcd)
        self.settings_dial = SettingsDial()
        self.alert_manager = AlertManager()

    def main(self):
        self.ultrasonic.establish_baseline_distance()

        while True:
            try:
                rotation_value = self.settings_dial.get_rotation()
                current_temp, current_humidity = self.dht.get_value()

                if self.lcd.lcd_state == LcdState.DASHBOARD:
                    self.lcd.render_dashboard(current_temp, current_humidity, 0)

                if self.lcd.lcd_state == LcdState.SETTINGS:
                    if rotation_value == 1:
                        self.lcd.next_setting()
                    elif rotation_value == -1:
                        self.lcd.previous_setting()

                    self.lcd.render_settings_option()

                self.cycle_btn.tick()
                self.select_btn.tick()

                motion_detected = self.ultrasonic.is_detected()

                self.dht.temp = current_temp
                self.dht.humidity = current_humidity

                high_temp: bool = current_temp > 28
                high_humidity = current_humidity > 60

                if high_temp:
                    self.alert_manager.trigger_alert(alert_type=AlertType.HIGH_TEMP, message="Temp warning")
                else:
                    self.alert_manager.auto_resolve_alert(alert_type=AlertType.HIGH_TEMP)
                if high_humidity:
                    self.alert_manager.trigger_alert(alert_type=AlertType.HIGH_HUM, message="Humidity warning")
                else:
                    self.alert_manager.auto_resolve_alert(alert_type=AlertType.HIGH_HUM)
                if motion_detected:
                    self.alert_manager.trigger_alert(alert_type=AlertType.MOTION, message="Motion detected")
                else:
                    self.alert_manager.auto_resolve_alert(alert_type=AlertType.MOTION)

                high_climate: bool = high_temp and high_humidity
                self.led.led_on = motion_detected or high_climate

                time.sleep(0.1)

            except IOError:
                print("IOError")
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main = Main()
    main.main()
