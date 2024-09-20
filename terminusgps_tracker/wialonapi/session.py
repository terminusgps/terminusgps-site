from os import getenv
from typing import Optional

from wialon.api import Wialon, WialonError

import terminusgps_tracker.wialonapi.flags as flag

class WialonSession:
    def __init__(self, **kwargs) -> None:
        self.token = kwargs.get("token", None)
        self.wialon_api: Wialon = Wialon()

    @property
    def id(self) -> str | None:
        return self.wialon_api.sid

    def __enter__(self) -> "WialonSession":
        try:
            self.login(token=self.token)
        except WialonError as e:
            raise e
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.logout()

    def get_id_from_iccid(self, iccid: str) -> str | None:
        try:
            response = self.wialon_api.core_search_items(**{
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_unique_id",
                    "propValueMask": f"={iccid}",
                    "sortType": "sys_unique_id",
                    "propType": "property",
                    "or_logic": 0,
                },
                "force": 0,
                "flags": flag.DATAFLAG_UNIT_BASE,
                "from": 0,
                "to": 0,
            })
        except WialonError as e:
            raise e
        else:
            if response.get("totalItemsCount", 0) != 1:
                return None
            return response["items"][0].get("id")

    def refresh_session(self, operate_as: Optional[str] = None) -> None:
        """Refreshes the Wialon API session without logging out, and re-sets the session id attribute."""
        try:
            login_response: dict = self.wialon_api.core_duplicate(**{
                "operateAs": operate_as if operate_as else "",
                "continueCurrentSession": False,
            })
        except WialonError as e:
            raise e
        else:
            self.wialon_api.sid = login_response.get("eid")

    def login(self, token: Optional[str] = None) -> None:
        """Logs into the Wialon API and starts a new session."""
        if token:
            self.token: str = token
        elif getenv("WIALON_API_TOKEN") is not None:
            self.token: str = getenv("WIALON_API_TOKEN", "")
        else:
            raise ValueError("No Wialon API token provided or found in environment variable `WIALON_API_TOKEN`.")

        try:
            login_response: dict = self.wialon_api.token_login(**{
                "token": self.token,
                "fl": 0x1,
            })
        except WialonError as e:
            raise e
        else:
            self.wialon_api.sid = login_response.get("eid")
            if not login_response.get("user", {}):
                self.username = login_response.get("au")
            else:
                self.username = login_response.get("user", {}).get("nm")
            print(f"Logged into session as {self.username}:", self.wialon_api.sid)


    def logout(self) -> None:
        """Logs out of the Wialon API and raises an error if the session was not destroyed."""
        logout_response: dict = self.wialon_api.core_logout({})
        if logout_response.get("error") != 0:
            raise ValueError(f"Failed to properly logout of Wialon session #{self.id}")

def main() -> None:
    # Easily create and destroy Wialon sessions using Python's context managers
    ## With environment variable token. Default behavior
    with WialonSession() as session:
        print(f"Logged in as: {session.username}")
        print(f"Session ID: #{session.id}")
        result = session.wialon_api.core_check_unique(**{"type": "user", "value": "Terminus-1000"})
        print(result)

    ## With plaintext token
    with WialonSession(token=getenv("WIALON_PETER_TOKEN")) as session:
        print(f"Logged in as: {session.username}")
        print(f"Session ID: #{session.id}")
        result = session.wialon_api.core_check_unique(**{"type": "user", "value": "Terminus-1000"})
        print(result)

if __name__ == "__main__":
    main()
