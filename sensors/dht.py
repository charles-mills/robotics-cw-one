import math
import config

import grovepi
from managers import AlertManager, AlertType

class Dht:
    def __init__(self, port: int, alert_manager: AlertManager):
        self.port: int = port
        self.type: int = 0
        self.alert_manager: AlertManager = alert_manager
        self._temp: float = 0
        self._humidity: float = 0
        self._last_temp: float = 0
        self._last_humidity: float = 0
        self._using_last_temp: bool = False
        self._using_last_humidity:bool = False

    def tick(self) -> None:
        """
        Polls the DHT11 sensor for new temperature and humidity data.
        It also, include logic for NaN readings where if caught it uses the last known reading.
        Likewise, it triggers or auto-resolves HIGH_TEMP and HIGH_HUM alerts based on config threshold.
        """
        self._last_temp = self._temp
        self._last_humidity = self._humidity

        self._temp, self._humidity = grovepi.dht(self.port, self.type)

        if self._humidity < 0 or self._humidity > 100 or math.isnan(self._humidity):
            self._humidity = self._last_humidity
            self._using_last_humidity = True
        else:
            self._using_last_humidity = False

        if self._temp < -100 or self._temp > 100 or math.isnan(self._temp):
            self._temp = self._last_temp
            self._using_last_temp = True
        else:
            self._using_last_temp = False

        if self._temp > config.HIGH_TEMP_C:
            self.alert_manager.trigger_alert(AlertType.HIGH_TEMP, "Temp warning", False)
        else:
            self.alert_manager.auto_resolve_alert(AlertType.HIGH_TEMP)

        if self._humidity > config.HIGH_HUMIDITY_PERCENT:
            self.alert_manager.trigger_alert(AlertType.HIGH_HUM, "Humidity warning", False)
        else:
            self.alert_manager.auto_resolve_alert(AlertType.HIGH_HUM)

    # tuple[] is not compatible with the Python version of the GrovePi
    def get_value(self):  # -> tuple[float, float]:
        """
        Retrieves the raw reading from the sensor.

        Returns:
            Tuple: Returns a tuple containing temperature and humidity as a float.
        """
        return grovepi.dht(self.port, self.type)

    @property
    def temp(self) -> float:
        """
        Gets the current temperature reading.

        Returns:
            float: The temperature value.
        """
        return self._temp

    @property
    def humidity(self) -> float:
        """
        Gets the current humidity reading.

        Returns:
            float: The humidity value.
        """
        return self._humidity

    @temp.setter
    def temp(self, value: float) -> None:
        """
        Overrides the internal temperature values.

        Args:
            value (float): The new temperature value.
        """
        self._temp = value

    @humidity.setter
    def humidity(self, value: float) -> None:
        """
        Overrides the internal humidity value.

        Args:
            value (float): The new humidity value.
        """
        self._humidity = value
