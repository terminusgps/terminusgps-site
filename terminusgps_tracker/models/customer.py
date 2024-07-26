from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.models.asset import WialonAsset


class Customer(models.Model):
    class Meta:
        db_table_comment = "A customer is a user who has access to the Wialon API."
        default_permissions = ["add", "change", "view"]
        permissions = [
            ("can_use_wialon_api", _("Can use Wialon API.")),
        ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(
        WialonAsset,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.user.username
