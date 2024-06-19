from django.db import models

from payments.models.tokens.base import BaseTokenModel


class LightmetricsToken(BaseTokenModel):
    _id_token = models.TextField(null=True, blank=True, default=None)

    @property
    def id_token(self) -> str:
        if not self._id_token:
            raise ValueError("ID token is unset.")
        return self._decrypt_token(self._id_token)

    @id_token.setter
    def id_token(self, value: str) -> None:
        self._id_token = self._encrypt_token(value)
