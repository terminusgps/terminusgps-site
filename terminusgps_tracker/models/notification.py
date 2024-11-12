from django.db import models
from django.utils.translation import gettext_lazy as _


class TrackerNotification(models.Model):
    class NotificationMethod(models.TextChoices):
        PHONE = "call", _("Notification via phone call")
        SMS = "sms", _("Notification via sms")

    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    body = models.CharField(max_length=512)
    method = models.CharField(
        max_length=4, choices=NotificationMethod.choices, default=NotificationMethod.SMS
    )
    phone = models.CharField(max_length=15)

    def __str__(self) -> str:
        return self.name
