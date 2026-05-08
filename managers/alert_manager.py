import time
import requests
from dataclasses import dataclass, field
from enum import Enum, auto

import config

class AlertType(Enum):
    MOTION = auto()
    HIGH_TEMP = auto()
    HIGH_HUM = auto()
    ANY = auto()

LastNotification = {
    AlertType.MOTION: 0.0,
    AlertType.HIGH_TEMP: 0.0,
    AlertType.HIGH_HUM: 0.0,
    AlertType.ANY: 0.0,
}

@dataclass
class Alert:
    alert_type: AlertType
    message: str
    dismissal_required: bool
    timestamp: str = field(default_factory=lambda: time.strftime("%H:%M", time.localtime()))


def _push_alert(alert: Alert) -> bool:
    now = time.monotonic()

    if now - LastNotification[alert.alert_type] < config.NOTIFICATION_COOLDOWN:
        return False

    # ANY is currently unused but can add a path for this
    LastNotification[alert.alert_type] = now
    LastNotification[AlertType.ANY] = now

    try:
        requests.post(config.NTFY_URL, data=alert.message.encode("utf-8"), headers=
        {
            "Title": f"Security System: {alert.alert_type.name}",
            "Priority": "5",
            "Tags": "warning",
        },
        timeout=5
        )
        return True
    except requests.RequestException as e:
        print(f"Failed to push alert: {e}")
        return False


class AlertManager:

    def __init__(self):
        self._active_alerts: list[Alert] = []

    def trigger_alert(self, alert_type: AlertType, message: str, dismissal_required: bool) -> None:
        """
        Inserts a new alert into the list of active alerts.
        The start of the list represents the latest alert.

        Args:
            alert_type (AlertType): What kind of alert it is e.g. Temperature, motion detected etc.
            message (str): What string should be displayed along with the alert.
            dismissal_required (bool): Should the user be able to dismiss the alert.
        """

        for alert in self._active_alerts:
            if alert.alert_type == alert_type:
                return

        new_alert = Alert(alert_type, message, dismissal_required)
        self._active_alerts.insert(0, new_alert)
        _push_alert(new_alert)

    def auto_resolve_alert(self, alert_type: AlertType) -> None:
        """ 
        Auto removes any alerts that should not be in the active alerts list.

        Args:
            alert_type (AlertType): What type of alert should be removed.
        """

        self._active_alerts = [i for i in self._active_alerts if i.alert_type != alert_type]

    def try_resolve_alerts(self, dht_temp: float, dht_humidity: float) -> None:
        """
        Checks whether current values are below the required threshold to remove alerts for temp and humidity

        """

        if dht_temp <= config.TEMPERATURE_RESOLVE_THRESHOLD:
            self.auto_resolve_alert(AlertType.HIGH_TEMP)
        if dht_humidity <= config.HUMIDITY_RESOLVE_THRESHOLD:
            self.auto_resolve_alert(AlertType.HIGH_HUM)

    @property
    def current_alert(self) -> Alert:
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


    def dismiss_alert(self) -> None:
        """
        Dismisses any ultrasonic alerts that require the user to press the select button.

        Returns:
            None
        """
        if not self._active_alerts:
            return
        
        current_alert_to_display = self._active_alerts[0]

        if current_alert_to_display.dismissal_required:
            self._active_alerts.pop(0)

    @property
    def active_alerts(self):
        return self._active_alerts