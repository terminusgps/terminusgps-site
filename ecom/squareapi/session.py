from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
from os import environ as env

class SquareSession:
    def __init__(self) -> None:
        self.client = Client(
            bearer_auth_credentials=BearerAuthCredentials(
                access_token=env["SQUARE_ACCESS_TOKEN"],
            ),
            environment="sandbox"
        )

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> str | None:
        if exc_type:
            return f"An error occurred: {exc_value}"
