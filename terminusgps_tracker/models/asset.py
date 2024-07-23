from django.db import models
from django.utils.translation import gettext_lazy as _

class WialonAsset(models.Model):
    class ItemType(models.TextChoices):
        HARDWARE = "HDW", _("Hardware")
        RESOURCE = "RES", _("Resource")
        UNIT = "UNT", _("Unit")
        UNIT_GROUP = "UGR", _("Unit Group")
        USER = "USR", _("User")
        ROUTE = "RTE", _("Route")

    id = models.PositiveBigIntegerField(unique=True, primary_key=True)
    uuid = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=255, null=True, default=None)
    item_type = models.CharField(
        max_length=3,
        choices=ItemType.choices,
        default=ItemType.UNIT,
    )

    def __str__(self) -> str:
        return f"{self.name} - #{self.id}"

    def save(self, *args, **kwargs) -> None:
        if self.id is None and self.uuid is None:
            raise ValueError("ID and UUID are unset.")
        elif self.id is None:
            raise ValueError("ID is unset.")
        elif self.uuid is None:
            raise ValueError("UUID is unset.")

        if self.name is None:
            self.name = str(self.uuid)

        super().save(*args, **kwargs)

