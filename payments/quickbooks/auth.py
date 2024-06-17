from typing import Optional

from django.conf import settings
from django.contrib.auth.models import User
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes


class QuickbooksAuthClient:
    def __init__(self, user: User, access_token: Optional[str] = None) -> None:
        self._client_id = settings.QUICKBOOKS.get("CLIENT_ID")
        self._client_secret = settings.QUICKBOOKS.get("CLIENT_SECRET")
        self._environment = settings.QUICKBOOKS.get("ENVIRONMENT")
        self._redirect_uri = settings.QUICKBOOKS.get("REDIRECT_URI")
        self.authorization_flow(user, access_token=access_token)

        return None

    @property
    def scopes(self) -> list[Scopes]:
        return [
            Scopes.ACCOUNTING,
            Scopes.EMAIL,
            Scopes.PAYMENT,
            Scopes.PROFILE,
        ]

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @property
    def environment(self) -> str:
        return self._environment

    @property
    def redirect_uri(self) -> str:
        return self._redirect_uri

    def _create_auth_client(self, access_token: Optional[str] = None) -> AuthClient:
        if not access_token:
            return AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                environment=self.environment,
                redirect_uri=self.redirect_uri,
            )
        else:
            return AuthClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                environment=self.environment,
                redirect_uri=self.redirect_uri,
                access_token=access_token,
            )

    def authorization_flow(
        self, user: User, access_token: Optional[str] = None
    ) -> None:
        self.auth_client = self._create_auth_client(access_token)
        if self.auth_client.access_token:
            pass
        else:
            self.auth_url = self.auth_client.get_authorization_url(self.scopes)
