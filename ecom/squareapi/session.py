from django.conf import settings

from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client

from typing import Union


class SquareSession:
    def __init__(self) -> None:
        self.client = Client(
            bearer_auth_credentials=BearerAuthCredentials(
                access_token=settings.SQUARE_API_ACCESS_TOKEN,
            ),
            environment="sandbox",
        )

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb) -> Union[str, None]:
        if exc_type:
            return f"An error occurred: {exc_value}"
        return
