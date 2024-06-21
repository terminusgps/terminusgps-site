from django.conf import settings
from django.db import models
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks

from .token import BaseToken

DEFAULT_QUICKBOOKS_SCOPES = [
    Scopes.ACCOUNTING,
    Scopes.EMAIL,
    Scopes.OPENID,
    Scopes.PAYMENT,
]


class QuickbooksToken(BaseToken):
    redirect_uri = models.URLField(default=settings.QUICKBOOKS["REDIRECT_URI"])

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

    def _get_auth_url(
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
