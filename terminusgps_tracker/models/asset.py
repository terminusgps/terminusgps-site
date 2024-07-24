from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.signing import Signer

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
        if not self.name:
            self.name = str(self.uuid)

        super().save(*args, **kwargs)

class AuthToken:
    class ServiceType(models.TextChoices):
        WIALON = "WI", _("Wialon")
        QUICKBOOKS = "QB", _("Quickbooks")
        LIGHTMETRICS = "LM", _("Lightmetrics")

    _access_token = models.CharField(max_length=255)
    _refresh_token = models.CharField(max_length=255)
    expiry_date = models.DateTimeField(blank=True, null=True, default=None)
    service_type = models.CharField(
        max_length=2,
        choices=ServiceType.choices,
        default=ServiceType.WIALON,
    )

    def _sign_token(self, value: str) -> str:
        return Signer().sign(value)
    
    def _unsign_token(self, value: str) -> str:
        return Signer().unsign(value)
