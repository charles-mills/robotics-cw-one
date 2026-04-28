import grovepi
from managers import AlertManager, AlertType

HIGH_TEMP_C: float = 28
HIGH_HUMIDITY_PERCENT: float = 60


class Dht:
    def __init__(self, port: int, alert_manager: AlertManager):
        grovepi.set_bus("RPI_1")
        self.port: int = port
        self.type: int = 0
        self.alert_manager: AlertManager = alert_manager
        self._temp: float = 0
        self._humidity: float = 0
        self._last_temp: float = 0
        self._last_humidity: float = 0

        # Might not need these but thought it could be useful if we had some way of checking that we're using a fallback.
        self._using_last_temp: bool = False
        self._using_last_humidity:bool = False

    def tick(self) -> None:
        self._last_temp = self._temp
        self._last_humidity = self._humidity

        self._temp, self._humidity = grovepi.dht(self.port, self.type)

        if self._humidity < 0 or self._humidity > 100:
            self.humidity = self._last_humidity
            self._using_last_humidity = True
        else:
            self._using_last_humidity = False

        if self._temp < -100 or self._temp > 100:
            self._temp = self._last_temp
            self._using_last_temp = True
        else:
            self._using_last_temp = False

        if self._temp > HIGH_TEMP_C:
            self.alert_manager.trigger_alert(AlertType.HIGH_TEMP, "Temp warning", False)
        else:
            self.alert_manager.auto_resolve_alert(AlertType.HIGH_TEMP)

        if self._humidity > HIGH_HUMIDITY_PERCENT:
            self.alert_manager.trigger_alert(AlertType.HIGH_HUM, "Humidity warning", False)
        else:
            self.alert_manager.auto_resolve_alert(AlertType.HIGH_HUM)

    # tuple[] is not compatible with the Python version of the GrovePi
    def get_value(self):  # -> tuple[float, float]:
        # [temp, humidity] = grovepi.dht(self.port, type)
        return grovepi.dht(self.port, self.type)

    @property
    def temp(self) -> float:
        return self._temp

    @property
    def humidity(self) -> float:
        return self._humidity

    @temp.setter
    def temp(self, value: float) -> None:
        self._temp = value

    @humidity.setter
    def humidity(self, value: float) -> None:
        self._humidity = value
