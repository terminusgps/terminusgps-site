from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from django.conf import settings


class QuickbooksClient(AuthClient):
    def __init__(self) -> None:
        super().__init__(
            client_id=settings.QUICKBOOKS.CLIENT_ID,
            client_secret=settings.QUICKBOOKS.CLIENT_SECRET,
            redirect_uri=settings.QUICKBOOKS.REDIRECT_URI,
            environment=settings.QUICKBOOKS.ENVIRONMENT,
        )
