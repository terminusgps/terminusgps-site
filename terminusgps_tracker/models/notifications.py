from datetime import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from terminusgps.wialon.session import WialonSession


class TrackerNotification(models.Model):
    class NotificationTriggerBehavior(models.TextChoices):
        FIRST_MSG = str(0x0), _("First message")
        EVERY_MSG = str(0x1), _("Every message")
        DISABLED = str(0x2), _("Disabled")

    class NotificationActionType(models.TextChoices):
        EMAIL = "email", _("Notify by email")
        SMS = "sms", _("Notify by SMS")
        ONLINE = "online", _("Pop-up window on hosting")
        MOBILE = "mobile", _("Mobile app")
        REQUEST = "request", _("HTTP Request")
        TELEGRAM = "telegram", _("Notify by Telegram")
        REGISTER = "register", _("Register event for unit")
        EXECUTE = "execute", _("Execute a command")
        VIDEO = "video", _("Upload a video")
        ACCESS = "access", _("Update unit access")
        SET_COUNTER = "set_counter", _("Set a counter value")
        STORE_COUNTER = "store_counter", _("Store a counter value")
        STATUS = "status", _("Update a unit's status")
        UNIT_GROUP = "unit_group", _("Update a unit group")
        REPORT = "report", _("Send a report via email")
        ROUND = "round", _("Create a round")
        DRIVER = "driver", _("Reset driver")
        TRAILER = "trailer", _("Reset trailer")

    name = models.CharField(max_length=128)
    text = models.TextField(max_length=2048, null=True, blank=True, default=None)
    action = models.CharField(
        max_length=16,
        choices=NotificationActionType.choices,
        default=NotificationActionType.REQUEST,
    )
    trigger = models.CharField(
        max_length=3,
        choices=NotificationTriggerBehavior.choices,
        default=NotificationTriggerBehavior.EVERY_MSG,
    )
    wialon_id = models.BigIntegerField(default=None, null=True, blank=True)
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        if not self.wialon_id and session:
            self.wialon_id = self.wialon_create_notification(session)
        return super().save(**kwargs)

    def enable(self, session: WialonSession) -> None:
        session.wialon_api.resource_update_notification(
            **{
                "itemId": self.profile.wialon_resource_id,
                "id": self.wialon_id,
                "callMode": "enable",
                "e": int(True),
            }
        )

    def disable(self, session: WialonSession) -> None:
        session.wialon_api.resource_update_notification(
            **{
                "itemId": self.profile.wialon_resource_id,
                "id": self.wialon_id,
                "callMode": "enable",
                "e": int(False),
            }
        )

    def wialon_create_notification(
        self,
        session: WialonSession,
        units: list[str],
        start: float | None = None,
        end: float | None = None,
        timeout: int = 5,
        alert_duration: int = 1,
        alert_duration_prev: int = 1,
        max_alarms: int = 0,
        max_time_between: int = 0,
        control_period: int = 1,
        tz: str | None = None,
        lang: str = "en",
    ) -> int:
        now = timezone.now()
        start = start or datetime.timestamp(now)
        end = end or datetime.timestamp(now + datetime.timedelta(days=30))
        tz = tz or timezone.get_current_timezone_name()

        response = session.wialon_api.resource_update_notification(
            **{
                "itemId": self.profile.wialon_resource_id,
                "id": 0,
                "callMode": "create",
                "n": self.name,
                "txt": self.text,
                "ta": start,
                "td": end,
                "ma": max_alarms,
                "mmtd": max_time_between,
                "cdt": timeout,
                "mast": alert_duration,
                "mpst": alert_duration_prev,
                "cp": control_period,
                "fl": self.trigger,
                "tz": tz,
                "la": lang,
                "un": units,
            }
        )
        return int(response[0])
