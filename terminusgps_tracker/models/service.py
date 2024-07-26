from typing import Union
from urllib.parse import urlencode

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuthService(models.Model):
    class AuthServiceName(models.TextChoices):
        WIALON = "WI", _("Wialon Hosting")
        QUICKBOOKS = "QB", _("Quickbooks")
        LIGHTMETRICS = "LM", _("Lightmetrics")
        FLEETRUN = "FR", _("Fleetrun")
        SURFSIGHT = "SI", _("Surfsight")

    name = models.CharField(
        max_length=2,
        choices=AuthServiceName.choices,
        default=AuthServiceName.WIALON,
    )

    def __str__(self) -> str:
        return self.name.title()

    def _generate_auth_url(self) -> str:
        params = urlencode({"client_id": "terminusgps.com"})
        match self.name:
            case AuthService.AuthServiceName.WIALON:
                url = "https://hosting.terminusgps.com/login.html?"
            case AuthService.AuthServiceName.QUICKBOOKS:
                url = "http://localhost:8000/?"
            case _:
                url = "https://localhost:8000/?"

        return url + params

    @property
    def auth_url(self) -> str:
        return self._generate_auth_url()

class AuthServiceImage(models.Model):
    name = models.CharField(max_length=255)
    service = models.ForeignKey(AuthService, on_delete=models.CASCADE)
    source = models.ImageField(upload_to="services")

    def __str__(self) -> str:
        return f"{self.service} Image #{self.id}"

class AuthToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(AuthService, on_delete=models.CASCADE)
    _access_token = models.CharField(max_length=255)
    _refresh_token = models.CharField(max_length=255)
    _auth_code = models.CharField(max_length=255)
    _token_type = models.CharField(max_length=255, default="Bearer")

    def _sign_value(self, value: str) -> str:
        signer = Signer()
        return signer.sign(value)

    def _unsign_value(self, value: str) -> str:
        signer = Signer()
        return signer.unsign(value)

    def _encrypt_value(self, value: str) -> str:
        f = Fernet(settings.ENCRYPTION_KEY)
        signed_value = self._sign_value(value)
        return f.encrypt(signed_value.decode()).encode()

    def _decrypt_value(self, value: str) -> str:
        f = Fernet(settings.ENCRYPTION_KEY)
        decrypted_value = f.decrypt(value.encode()).decode()
        return self._unsign_value(decrypted_value)

    @property
    def access_token(self) -> Union[str, None]:
        if not self._access_token:
            return None
        return self._decrypt_value(self._access_token)

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token = self._encrypt_value(value)

    @property
    def refresh_token(self) -> Union[str, None]:
        if not self._refresh_token:
            return None
        return self._decrypt_value(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value: str) -> None:
        self._refresh_token = self._encrypt_value(value)

    @property
    def auth_code(self) -> Union[str, None]:
        if not self._auth_code:
            return None
        return self._decrypt_value(self._auth_code)

    @auth_code.setter
    def auth_code(self, value: str) -> None:
        self._auth_code = self._encrypt_value(value)
