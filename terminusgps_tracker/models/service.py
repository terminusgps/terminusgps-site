from typing import Union

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oauthlib.oauth2 import WebApplicationClient


class AuthService(models.Model):
    class ServiceType(models.TextChoices):
        WIALON = "WI", _("Wialon Hosting")
        QUICKBOOKS = "QB", _("Quickbooks")
        LIGHTMETRICS = "LM", _("Lightmetrics")
        FLEETRUN = "FR", _("Fleetrun")
        SURFSIGHT = "SI", _("Surfsight")

    _access_token = models.CharField(max_length=255, null=True, default=None)
    _refresh_token = models.CharField(max_length=255, null=True, default=None)
    _auth_code = models.CharField(max_length=255, null=True, default=None)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, null=True, blank=True, default=None)
    expiry_date = models.DateTimeField(blank=True, null=True, default=None)
    service_type = models.CharField(
        max_length=2,
        choices=ServiceType.choices,
        default=ServiceType.WIALON,
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s {self.service_type.title()} token"

    def __repr__(self) -> str:
        return f"AuthService(user='{self.user.username}', state='{self.state}', expiry_date={self.expiry_date}, service_type='{self.service_type.title()}')"

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

    def is_expired(self) -> bool:
        return self.expiry_date is not None and self.expiry_date < timezone.now()

    def get_client(self, id: str, **kwargs) -> WebApplicationClient:
        return WebApplicationClient(
            client_id=id,
            code=self.auth_code,
            **kwargs,
        )

    def get_redirect_uri(self) -> Union[str, None]:
        match self.service_type:
            case AuthService.ServiceType.WIALON:
                redirect_uri = settings.WIALON_REDIRECT_URI
            case AuthService.ServiceType.QUICKBOOKS:
                redirect_uri = settings.QUICKBOOKS_REDIRECT_URI
            case AuthService.ServiceType.LIGHTMETRICS:
                redirect_uri = settings.LIGHTMETRICS_REDIRECT_URI
            case _:
                redirect_uri = None

        return redirect_uri

class AuthServiceImage(models.Model):
    class ImageName(models.TextChoices):
        LOGO = "LO", _("Logo")
        ICON = "IC", _("Icon")
        BANNER = "BA", _("Banner")
        RESOURCE = "RE", _("Resource")

    source = models.ImageField(upload_to="services")
    service_type = models.CharField(
        max_length=2,
        choices=AuthService.ServiceType.choices,
        default=AuthService.ServiceType.WIALON,
    )
    image_type = models.CharField(
        max_length=2,
        choices=ImageName.choices,
        default=ImageName.RESOURCE,
    )

    def __str__(self) -> str:
        return f"{self.service_type} Image #{self.id}"
