from django.db import models
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items import WialonUnitGroup, WialonResource


class TerminusNotification(models.Model):
    class NotificationMethod(models.TextChoices):
        PHONE = "call", _("Notification via phone call")
        SMS = "sms", _("Notification via sms")

    name = models.CharField(max_length=64)
    body = models.CharField(max_length=256)
    profile = models.ForeignKey(
        "TrackerProfile", on_delete=models.CASCADE, related_name="notifications"
    )
    method = models.CharField(
        max_length=4, choices=NotificationMethod.choices, default=NotificationMethod.SMS
    )
    phone = models.CharField(max_length=15)
    wialon_id = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self) -> str:
        return f"'{self.name}' for {self.profile.user.username}"

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        if session is None:
            return super().save(**kwargs)

        resource_id: str = str(self.profile.wialon_resource_id)
        group_id: str = str(self.profile.wialon_group_id)
        if resource_id and group_id:
            wialon_group = WialonUnitGroup(id=group_id, session=session)
            wialon_resource = WialonResource(id=resource_id, session=session)
            self.wialon_id = wialon_resource.create_notification(
                method=self.method, name=self.name, body=self.body, group=wialon_group
            )
        return super().save(**kwargs)
