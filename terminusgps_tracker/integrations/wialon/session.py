from os import getenv
from typing import Any

from django.conf import settings
from wialon import Wialon, WialonError

from terminusgps_tracker.integrations.wialon.errors import (
    WialonLoginError,
    WialonTokenNotFoundError,
)


class WialonSession:
    def __init__(self, token: str | None = None, sid: str | None = None) -> None:
        self.token = token
        self.wialon_api = Wialon(sid=sid)

    @property
    def id(self) -> str | None:
        return self.wialon_api.sid

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value: str | None) -> None:
        self._token = value if value else settings.WIALON_API_TOKEN

    def __enter__(self) -> "WialonSession":
        if not self.wialon_api.sid:
            self.login(self.token)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.logout()
        return

    def _deconstruct_login_response(self, login_response: dict) -> None:
        self.wialon_api.sid = login_response.get("eid", "")
        self.username = login_response.get("user", {}).get("nm")
        self.uid = login_response.get("user", {}).get("id")
        self.base_url = login_response.get("base_url", "")
        self.gis_sid = login_response.get("gis_sid", "")
        self.host = login_response.get("host", "")
        self.hw_gp_ip = login_response.get("hw_gw_ip", "")
        self.video_service_url = login_response.get("video_service_url", "")
        self.wsdk_version = login_response.get("wsdk_version", "")
        return

    def login(self, token: str | None = None) -> None:
        """Logs into the Wialon API and starts a new session."""
        if not token:
            raise WialonTokenNotFoundError(token=token, wialon_error=None)
        try:
            login_response = self.wialon_api.token_login(
                **{"token": self.token, "fl": sum([0x1, 0x2, 0x20])}
            )
        except WialonError as e:
            raise WialonLoginError(token=self.token, wialon_error=e)
        else:
            self._deconstruct_login_response(login_response)
            print(f"Logged into session #{self.wialon_api.sid} as '{self.username}'")

    def logout(self) -> None:
        """Logs out of the Wialon API and raises an error if the session was not destroyed."""
        sid = str(self.wialon_api.sid)
        logout_response = self.wialon_api.core_logout({})

        if logout_response.get("error") == 0:
            print(f"Logged out of session #{sid} as '{self.username}'")
        else:
            print(f"Failed to properly destroy session #{sid}")


def main() -> None:
    # Easily create and destroy Wialon sessions using Python's context managers
    ## With environment variable token. Default behavior
    with WialonSession() as session:
        result = session.wialon_api.core_check_unique(
            **{"type": "user", "value": "Terminus-1000"}
        )
        print(result)

    ## With plaintext token
    with WialonSession(getenv("PETER_WIALON_TOKEN")) as session:
        result = session.wialon_api.core_check_unique(
            **{"type": "user", "value": "Terminus-1000"}
        )
        print(result)


if __name__ == "__main__":
    main()
