from os import getenv
from typing import Optional, Any

from django.conf import settings
from wialon import Wialon

from terminusgps_tracker.wialonapi.errors import WialonTokenNotFoundError


class WialonSession:
    def __init__(self, wialon_api_token: Optional[str] = None) -> None:
        self._token = wialon_api_token
        self.wialon_api = Wialon()

    @property
    def id(self) -> str | None:
        return self.wialon_api.sid

    @property
    def token(self) -> str | None:
        if not self._token:
            self._token = settings.WIALON_API_TOKEN
        return self._token

    def __enter__(self) -> "WialonSession":
        self.login(token=self.token)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.logout()
        return

    def _deconstruct_login_response(self, login_response: dict) -> None:
        if not login_response.get("user", {}):
            self.username = login_response.get("au")
        else:
            self.username = login_response.get("user", {}).get("nm")
            self.uid = login_response.get("user", {}).get("id")
        self.wialon_api.sid = login_response.get("eid", "")
        self.base_url = login_response.get("base_url", "")
        self.gis_sid = login_response.get("gis_sid", "")
        self.host = login_response.get("host", "")
        self.hw_gp_ip = login_response.get("hw_gw_ip", "")
        self.video_service_url = login_response.get("video_service_url", "")
        self.wsdk_version = login_response.get("wsdk_version", "")
        return

    def login(self, token: Optional[str] = None) -> None:
        """Logs into the Wialon API and starts a new session."""
        if not token:
            raise WialonTokenNotFoundError(token=token, wialon_error=None)
        else:
            login_response: dict[str, Any] = self.wialon_api.token_login(
                token=self.token, fl=0x1
            )
            self._deconstruct_login_response(login_response)
            print(f"Logged into session #{self.wialon_api.sid} as '{self.username}'")
        return

    def logout(self) -> None:
        """Logs out of the Wialon API and raises an error if the session was not destroyed."""
        session_id = str(self.wialon_api.sid)
        logout_response: dict = self.wialon_api.core_logout({})
        if logout_response.get("error") == 0:
            print(f"Logged out of session #{session_id} as '{self.username}'")
        else:
            print(f"Failed to properly destroy session #{session_id}")


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
