from django.conf import settings
from django.db import models
from intuitlib.client import AuthClient

from payments.models.tokens.base import BaseTokenModel


class QuickbooksToken(BaseTokenModel):
    company_id = models.CharField(max_length=64, null=True, blank=True, default=None)
    redirect_uri = models.URLField(
        null=True, blank=True, default=settings.QUICKBOOKS["REDIRECT_URI"]
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s Quickbooks Token"

    def gen_auth_client(self) -> AuthClient:
        return AuthClient(
            access_token=self.access_token,
            client_id=settings.QUICKBOOKS.get("CLIENT_ID", ""),
            client_secret=settings.QUICKBOOKS.get("CLIENT_SECRET", ""),
            environment=settings.QUICKBOOKS.get("ENVIRONMENT", "sandbox"),
            redirect_uri=self.redirect_uri,
        )
