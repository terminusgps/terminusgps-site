import urllib.parse

from django.conf import settings
from django.db import models
from django.http import HttpResponse
from django.shortcuts import redirect

from .token import BaseToken


class WialonToken(BaseToken):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    username = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.user.username}'s Wialon Token"

    @property
    def auth_url(self) -> str:
        client_id = settings.WIALON_CLIENT_ID
        redirect_uri = settings.WIALON_REDIRECT_URI
        username = self.username
        params = {
            "client_id": client_id,
            "access_type": sum(
                [
                    0x100,  # online tracking
                    0x200,  # view access to most data
                    0x400,  # modification of non-sensitive data
                    0x800,  # modification of sensitive data
                ]
            ),
            "activation_time": 0,
            "duration": 2592000,  # 30 days
            "lang": "en",
            "flags": 0x1,
            "user": username,
            "response_type": "token",
            "redirect_uri": redirect_uri,
            "css_url": "",
        }
        encoded_params = urllib.parse.urlencode(params)
        return f"https://hosting.terminusgps.com/login.html?{encoded_params}"

    def authorize(self, auth_url: str) -> HttpResponse:
        return redirect(auth_url)
