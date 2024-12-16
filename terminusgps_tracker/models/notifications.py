from django.db import models


class TrackerNotification(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return self.name
