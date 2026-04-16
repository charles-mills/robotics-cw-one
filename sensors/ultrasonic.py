import grovepi
import time
import statistics


class Ultrasonic:
    """
    Initialises the Ultrasonic Ranger and processes its values.

    """

    def __init__(self, port: int) -> None:
        """
        Assigns the sensor port use and initialises the GrovePi bus.

        Args:
            port: GrovePi port the sensor is connected to.

        """
        grovepi.set_bus("RPI_1")
        self.port: int = port
        self.baseline: float = -1.0

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
        return self.get_value() < self.baseline
