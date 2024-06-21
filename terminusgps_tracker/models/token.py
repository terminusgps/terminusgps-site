from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks

DEFAULT_QUICKBOOKS_SCOPES = [
    Scopes.ACCOUNTING,
    Scopes.EMAIL,
    Scopes.OPENID,
    Scopes.PAYMENT,
]


class QuickbooksToken(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    _access_token = models.TextField(null=True, blank=True, default=None)
    _refresh_token = models.TextField(null=True, blank=True, default=None)
    token_expiry = models.DateTimeField(null=True, blank=True)
    redirect_uri = models.URLField(default=settings.QUICKBOOKS["REDIRECT_URI"])

    def _encrypt_token(self, token: str) -> str:
        # Encrypt token using Fernet symmetric encryption
        f = Fernet(settings.AUTH_ENCRYPTION_KEY)
        return f.encrypt(token.encode()).decode()

    def _decrypt_token(self, token: str) -> str:
        f = Fernet(settings.AUTH_ENCRYPTION_KEY)
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

    def _get_auth_client(self) -> AuthClient:
        if not self.access_token:
            client = AuthClient(
                client_id=settings.QUICKBOOKS.get("CLIENT_ID", ""),
                client_secret=settings.QUICKBOOKS.get("CLIENT_SECRET", ""),
                environment=settings.QUICKBOOKS.get("ENVRIONMENT", ""),
                redirect_uri=self.redirect_uri,
            )
        else:
            client = AuthClient(
                client_id=settings.QUICKBOOKS.get("CLIENT_ID", ""),
                client_secret=settings.QUICKBOOKS.get("CLIENT_SECRET", ""),
                environment=settings.QUICKBOOKS.get("ENVRIONMENT", ""),
                redirect_uri=self.redirect_uri,
                access_token=self.access_token,
            )
        return client

    def _gen_auth_url(
        self, auth_client: AuthClient, scopes: list[Scopes] = DEFAULT_QUICKBOOKS_SCOPES
    ) -> str:
        return auth_client.generate_authorization_url(scopes)

    def _get_client(self) -> QuickBooks:
        return QuickBooks(
            auth_client=self._get_auth_client(),
            refresh_token=self.refresh_token,
            company_id=settings.QUICKBOOKS.get("COMPANY_ID", ""),
            minorversion=70,
        )
