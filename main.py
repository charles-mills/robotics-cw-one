import time
import traceback
import paho.mqtt.publish as publish
import grovepi
from sympy import Point

from inputs import SelectButton, CycleButton
from managers import AlertManager
from outputs import Led, Fan, Lcd, Buzzer
from sensors import Ultrasonic, Dht

positions = [
    Point(-0.438, 0.125, 0.0025),
    Point(1.07, 0.164, 0.0025),
    Point(3.2, 0.0562, 0.0025),
    Point(2.47, 2.26, 0.0025),
    Point(3.48, 2.92, 0.0025),
    Point(1.1, 1.67, 0.0025),
    Point(0.425, 1.66, -0.00137),
    Point(0.553, 2.87, 0.00247)
]

def tick_component(comp):
    """
    Safely execute the tick method for single hardware components.

    Args:
        comp (_type_): Instantiated hardware component object.
    """
    try:
        comp.tick()
    except TypeError:
        print(f"Error while ticking")
        raise

def tick_components(components: list):
    """
    Iterates through a list of components and executes their tick methods.

    Args:
        components (list): A lisr of hardware component instance.
    """
    for comp in components:
        tick_component(comp)


class Main:
    INPUT_INTERVAL = 0.02
    ULTRASONIC_INTERVAL = 0.1
    DHT_INTERVAL = 2.0
    OUTPUT_INTERVAL = 0.1
    LCD_INTERVAL = 0.25
    PUBLISH_INTERVAL = 0.1
    LOOP_SLEEP = 0.005

    def __init__(self):
        self.alert_manager = AlertManager()

        self.ultrasonic = Ultrasonic(2, self.alert_manager)
        self.dht = Dht(3, self.alert_manager)
        self.led = Led(4, self.alert_manager)
        self.fan = Fan(5, self.alert_manager)
        self.lcd = Lcd(self.alert_manager, self.dht, self.ultrasonic)
        self.select_btn = SelectButton(6, self.lcd)
        self.cycle_btn = CycleButton(7, self.lcd)
        self.buzzer = Buzzer(8, self.alert_manager)

        self.input_components = [self.cycle_btn, self.select_btn]
        self.output_components = [self.led, self.fan, self.buzzer]

        grovepi.set_bus("RPI_1")

    def main(self):
        """
        The main lifecycle where it establishes sensor baseline, starts the run loop, catches exit signals and
        ensures a safe hardware shutdown on exit.

        """
        try:
            self.ultrasonic.establish_baseline_distance()
            self.run_loop()
        except KeyboardInterrupt:
            pass
        except TypeError:
            traceback.print_exc()
        finally:
            self.shutdown()

    def run_loop(self):
        """
        The continuous loop that uses time.monotonic() to track the elapsed time and calls tick commponents only when their
        specific polling intervals have passed.
        """
        now = time.monotonic()

        next_input_tick = now
        next_ultrasonic_tick = now
        next_dht_tick = now
        next_output_tick = now
        next_lcd_tick = now
        next_publish_tick = now

        while True:
            now = time.monotonic()

            if now >= next_input_tick:
                tick_components(self.input_components)
                next_input_tick = now + self.INPUT_INTERVAL

            if now >= next_ultrasonic_tick:
                tick_component(self.ultrasonic)
                next_ultrasonic_tick = now + self.ULTRASONIC_INTERVAL

            if now >= next_dht_tick:
                tick_component(self.dht)
                next_dht_tick = now + self.DHT_INTERVAL

            if now >= next_output_tick:
                tick_components(self.output_components)
                next_output_tick = now + self.OUTPUT_INTERVAL

            if now >= next_lcd_tick:
                tick_component(self.lcd)
                next_lcd_tick = now + self.LCD_INTERVAL

            if now >= next_publish_tick:
                publish.single("target_point", positions[0])

            time.sleep(self.LOOP_SLEEP)

    def shutdown(self):
        """
        Safely powers down hardware outputs and clears teh dispaly to prevent floating singals.
        """
        try:
            self.lcd.clear_display()
            self.led.led_on = False
            self.fan.set_value(0)
            self.buzzer.sound_state = False
        except TypeError:
            traceback.print_exc()


if __name__ == "__main__":
    main = Main()
    main.main()
