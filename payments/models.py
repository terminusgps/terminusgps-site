import os

from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from intuitlib.client import AuthClient

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "")


class AuthToken(models.Model):
    class Service(models.TextChoices):
        LIGHTMETRICS = "LM", _("Lightmetrics")
        QUICKBOOKS = "QB", _("Quickbooks")

    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    _access_token = models.TextField(null=True, blank=True, default=None)
    _refresh_token = models.TextField(null=True, blank=True, default=None)

    token_expiry = models.DateTimeField(null=True, blank=True)
    service = models.CharField(
        max_length=2,
        choices=Service.choices,
        default=Service.QUICKBOOKS,
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s Auth Token"

    def _encrypt_token(self, token: str) -> str:
        # Encrypt token using Fernet symmetric encryption
        f = Fernet(ENCRYPTION_KEY)
        return f.encrypt(token.encode()).decode()

    def _decrypt_token(self, token: str) -> str:
        f = Fernet(ENCRYPTION_KEY)
        return f.decrypt(token.encode()).decode()

    @property
    def access_token(self) -> str:
        if not self._access_token:
            raise ValueError("Access token is unset.")
        return self._decrypt_token(self._access_token)

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token = self._encrypt_token(value)

    @property
    def refresh_token(self) -> str:
        if not self._refresh_token:
            raise ValueError("Refresh token is unset.")
        return self._decrypt_token(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value: str) -> None:
        self._refresh_token = self._encrypt_token(value)


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = "CR", _("Order was created.")
        APPROVED = "AP", _("Order was approved by admin.")
        PAID = "PA", _("Order was paid by user.")
        CANCELED = "CA", _("Order was canceled.")

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.CREATED,
    )

    def __str__(self):
        return f"{self.user.username} - ${self.amount}"
