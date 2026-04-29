import statistics
import time

import grovepi
from managers import AlertManager, AlertType


class Ultrasonic:
    """
    Initialises the Ultrasonic Ranger and processes its values.

    """

    def __init__(self, port: int, alert_manager: AlertManager) -> None:
        """
        Assigns the sensor port use and initialises the GrovePi bus.

        Args:
            port: GrovePi port the sensor is connected to.

        """
        grovepi.set_bus("RPI_1")
        self.port: int = port
        self.baseline: float = -1.0
        self.alert_manager: AlertManager = alert_manager
        self._detection_timer: float = 0.0
        self._currently_detected: bool = False

    def establish_baseline_distance(self, seconds_to_read_for: float = 5.0) -> bool:
        """
        Establishes the median distance read by the ultrasonic ranger to establish a baseline for motion detection.

        Args:
            seconds_to_read_for: Number of seconds to sample for a baseline reading.

        Returns: True on assignment of the baseline to self.baseline.

        """
        readings: list[int] = []
        end_time: float = time.monotonic() + seconds_to_read_for

        pause_time: float = 0.1
        """
        Should be at least 0.1 seconds based on the example at:
        https://wiki.seeedstudio.com/Grove_-_Ultrasonic_Ranger
        
        'don't overload the i2c bus'
         
        """

        while time.monotonic() < end_time:
            readings.append(grovepi.ultrasonicRead(self.port))
            time.sleep(pause_time)

        self.baseline = statistics.median(readings)
        return True

    def get_value(self) -> int:
        """

        Returns: The raw value reading from the ultrasonic ranger.

        """
        return grovepi.ultrasonicRead(self.port)

    def is_detected(self) -> bool:
        """

        Returns: True if the reading of the ultrasonic ranger is below the established baseline, False otherwise.

        """
        return self.get_value() < (self.baseline - 5.0)

    def tick(self) -> None:
        if self.is_detected():
            if not self._currently_detected:
                self._currently_detected = True
                self._detection_timer = time.monotonic()

            elif time.monotonic() - self._detection_timer >= 0.3:
                self.alert_manager.trigger_alert(AlertType.MOTION, "Motion detected", True) 
                self._detection_timer = time.monotonic()

        else:
            self._currently_detected = False
 