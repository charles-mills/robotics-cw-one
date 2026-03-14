import grovepi
import time

class Ultrasonic:
    def __init__(self, port: int) -> None:
        grovepi.set_bus("RPI_1")
        self.port : int = port
        self.baseline : float = 0

    '''
    Establishes the average distance read by the sensor to establish a baseline
    for detection of motion.
    
    TODO: Requires some kind of outlier detection since it can often happen with the ultrasonic.
    '''
    def establish_baseline_distance(self, seconds_to_read_for : int = 5) -> float:
        distances : float = 0

        for s in range(0, seconds_to_read_for):
            distances += grovepi.ultrasonicRead(self.port)
            time.sleep(1) # replace !!

        return distances / seconds_to_read_for

    def is_beyond_baseline_for_seconds(self, seconds_to_detect : float = 0.1) -> bool:
        if self.baseline == 0:
            print("Baseline has not been configured or is 0.")
            return False

        interval = max(seconds_to_detect / 10, 0.1)
        above = 0

        for s in range(0, 10):
            grovepi.ultrasonicRead(self.port)

            if grovepi.ultrasonicRead(self.port) < self.baseline:
                above += 1

            time.sleep(interval)

        return above > 1 # bad pls fix

    def get_value(self):
        return grovepi.ultrasonicRead(self.port)
