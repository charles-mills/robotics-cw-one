import time
from dataclasses import dataclass
from enum import Enum, auto


class AlertType(Enum):
    MOTION = auto()
    HIGH_TEMP = auto()
    HIGH_HUM = auto()


@dataclass
class Alert:
    alert_type: AlertType
    message: str
    timestamp: float = time.time()


class AlertManager:

    def __init__(self):
        self._active_alerts: list[Alert] = []

    def trigger_alert(self, alert_type: AlertType, message: str) -> None:
        """
        Inserts a new alert into the list of active alerts.
        The start of the list represents the latest alert.

        Args:
            alert_type (AlertType): What kind of alert it is e.g. Temperature, motion detected etc.
            message (str): What string should be displayed along with the alert.
        """

        for alert in self._active_alerts:
            if alert.alert_type == alert_type:
                return

        new_alert = Alert(alert_type, message)
        self._active_alerts.insert(0, new_alert)

    def auto_resolve_alert(self, alert_type: AlertType) -> None:
        """ 
        Auto removes any alerts that should not be in the active alerts list.

        Args:
            alert_type (AlertType): What type of alert should be removed.
        """

        self._active_alerts = [i for i in self._active_alerts if i.alert_type != alert_type]

    @property
    def current_alert(self) -> Alert | None:
        if self._active_alerts:
            return self._active_alerts[0]

        return None

    @property
    def total_alert(self) -> int:
        return len(self._active_alerts)

    def has_alert_type(self, alert_type: AlertType) -> bool:
        for alert in self._active_alerts:
            if alert.alert_type == alert_type:
                return True
        return False
