from django.db import models

from payments.models.tokens.base import BaseTokenModel


class SquareToken(BaseTokenModel):
    def authorize(self) -> None:
        client_id = settings.SQUARE
