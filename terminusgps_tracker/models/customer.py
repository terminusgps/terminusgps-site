from django.db import models
from django.contrib.auth.models import User

from terminusgps_tracker.models.asset import WialonAsset
from terminusgps_tracker.validators import validate_item_type_user

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(
        WialonAsset,
        on_delete=models.CASCADE,
        validators=[validate_item_type_user]
    )

    def __str__(self) -> str:
        return self.user.username
