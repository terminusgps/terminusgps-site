from typing import Union

from django.core.signing import Signer
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from terminusgps_tracker.models.asset import WialonAsset
from terminusgps_tracker.validators import validate_item_type_user

class WialonToken(models.Model):
    _access_token = models.CharField(max_length=256)
    _refresh_token = models.CharField(max_length=256)
    expiry_date = models.DateTimeField(default=timezone.now)

    @property
    def access_token(self) -> str:
        signer = Signer(salt=self.id)
        return signer.unsign(self._access_token)

    @access_token.setter
    def access_token(self, value: str) -> None:
        signer = Signer(salt=self.id)
        self._access_token = signer.sign(value)

    @property
    def refresh_token(self) -> str:
        signer = Signer(salt=self.id)
        return signer.unsign(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value: str) -> None:
        signer = Signer(salt=self.id)
        self._refresh_token = signer.sign(value)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(
        WialonAsset,
        on_delete=models.CASCADE,
        validators=[validate_item_type_user]
    )

    def __str__(self) -> str:
        return self.user.username

    def set_access_token(self) -> None:
        if not hasattr(self.user, "auth_token"):
            self.user.auth_token = self.user.auth_token.create(user=self.user)

    def get_access_token(self) -> Union[str, None]:
        return self.user.auth_token.key if hasattr(self.user, "auth_token") else None
