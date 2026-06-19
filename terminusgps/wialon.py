import os

from django.conf import settings
from wialon.api import Wialon, WialonError


class WialonSession:
    def __init__(
        self,
        scheme: str = "https",
        host: str = "hst-api.wialon.com",
        port: int = 443,
        sid: str | None = None,
        token: str | None = None,
        username: str | None = None,
    ) -> None:
        self._uid = None
        self._wialon_api = Wialon(scheme=scheme, host=host, port=port, sid=sid)
        self._token = token or os.getenv("WIALON_TOKEN")
        self._username = username

    def __str__(self) -> str:
        return f"WialonSession #{self.id}"

    def __repr__(self) -> str:
        return f"{self.__class__}(sid={self.id})"

    def __enter__(self) -> "WialonSession":
        if self.id is None:
            if self._token:
                self.token_login(token=self._token, username=self._username)
            else:
                raise WialonError(-1, "Failed to login to the Wialon API")
        return self

    def __exit__(self, a, b, c) -> None:
        if self.id is not None:
            self.logout()

    def token_login(self, token: str, username: str | None = None) -> None:
        params = {"token": token, "flags": 0x3 if username else 0x1}
        if username is not None:
            params.update({"operateAs": username})
        response = self.wialon_api.token_login(**params)
        self.wialon_api.sid = response.get("eid")
        self._username = response.get("au")
        self._uid = response.get("user", {}).get("id")

    def logout(self) -> None:
        sid = self.wialon_api.sid
        if sid is not None:
            response = self.wialon_api.core_logout()
            if not int(response.get("error")) == 0:
                raise WialonError(
                    -1, f"Failed to logout of Wialon API session #{sid}"
                )
            self.wialon_api.sid = None

    @property
    def wialon_api(self):
        return self._wialon_api

    @property
    def uid(self):
        return self._uid

    @property
    def username(self):
        return self._username

    @property
    def id(self):
        return self.wialon_api.sid


def session_is_active(session: WialonSession) -> bool:
    """
    Returns whether a Wialon session is active.

    :param session: A Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
    :returns: Whether the session is active.
    :rtype: bool

    """
    try:
        session.wialon_api.avl_evts()
    except WialonError as error:
        if error._code == 1:
            return False
        raise
    else:
        return True


def get_session(sid: str | None = None) -> WialonSession:
    """
    Resumes and returns a Wialon session by session id.

    If ``sid`` wasn't provided or was invalid, starts a new session then returns it.

    :param sid: A Wialon API session id.
    :type sid: str | None
    :returns: A valid Wialon API session.
    :rtype: ~terminusgps.wialon.session.WialonSession

    """
    session = WialonSession(sid=sid)
    if session_is_active(session):
        return session
    else:
        session.token_login(token=settings.WIALON_TOKEN)
        return session


def get_vin_info(session: WialonSession, vin: str) -> dict:
    """
    Returns VIN # info from Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param vin: A VIN number.
    :type vin: str
    :returns: A dictionary of VIN # info.
    :rtype: dict

    """
    response = session.wialon_api.unit_get_vin_info(**{"vin": vin})
    return response["vin_lookup_result"]


def get_resource_choices(session: WialonSession) -> list[tuple]:
    """
    Returns a list of resources from Wialon as choice tuples.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :returns: A list of resource choice tuples.
    :rtype: list[tuple]

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_resource",
                "propName": "sys_name",
                "propValueMask": "*",
                "sortType": "sys_name",
                "propType": "property",
            },
            "from": 0,
            "to": 0,
            "force": 0,
            "flags": 1,
        }
    )
    return [(resource["id"], resource["nm"]) for resource in response["items"]]


def create_resource(
    session: WialonSession,
    creator_id: int,
    name: str,
    skip_creator_check: bool = False,
) -> int:
    """
    Creates a resource in Wialon and returns its id.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param creator_id: A Wialon user id.
    :type creator_id: int
    :param name: New resource name.
    :type name: str
    :param skip_creator_check: Whether to skip the creator check when creating the resource. Default is :py:obj:`False`.
    :type skip_creator_check: bool
    :returns: The new Wialon resource id.
    :rtype: int

    """
    response = session.wialon_api.core_create_resource(
        **{
            "creatorId": creator_id,
            "name": name,
            "dataFlags": 1,
            "skipCreatorCheck": int(skip_creator_check),
        }
    )
    return int(response["item"]["id"])


def create_user(
    session: WialonSession, creator_id: int, username: str, password: str
) -> int:
    """
    Creates a user in Wialon and returns its id.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param creator_id: A Wialon user id.
    :type creator_id: int
    :param name: New user name.
    :type name: str
    :param password: New user password.
    :type password: str
    :returns: The new Wialon user id.
    :rtype: int

    """
    response = session.wialon_api.core_create_user(
        **{
            "creatorId": creator_id,
            "name": username,
            "password": password,
            "dataFlags": 1,
        }
    )
    return int(response["item"]["id"])


def create_account(
    session: WialonSession, resource_id: int, plan: str
) -> None:
    """
    Creates an account from a resource in Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param resource_id: A Wialon resource id.
    :type resource_id: int
    :param plan: A Wialon billing plan.
    :type plan: str
    :returns: Nothing.
    :rtype: None

    """
    session.wialon_api.account_create_account(
        **{"itemId": resource_id, "plan": plan}
    )


def disable_account(session: WialonSession, resource_id: int) -> None:
    """
    Disables an account in Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param resource_id: A Wialon resource (account) id.
    :type resource_id: int
    :returns: Nothing.
    :rtype: None

    """
    session.wialon_api.account_enable_account(
        **{"itemId": resource_id, "enable": 0}
    )


def enable_account(session: WialonSession, resource_id: int) -> None:
    """
    Enables an account in Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.session.WialonSession
    :param resource_id: A Wialon resource (account) id.
    :type resource_id: int
    :returns: Nothing.
    :rtype: None

    """
    session.wialon_api.account_enable_account(
        **{"itemId": resource_id, "enable": 1}
    )


def create_new_account_user(username: str) -> int:
    """
    Creates a resource, user and an account then returns the user id.

    :param username: New user name.
    :type username: str
    :param password: New user password.
    :type password: str
    :returns: The Wialon user id.
    :rtype: int

    """
    session = get_session(sid=None)
    # User *must* change password on first login
    user_id = create_user(session, int(session.uid), username, "Terminus#1!")
    resource_id = create_resource(session, user_id, f"account_{username}")
    create_account(session, resource_id, plan="terminusgps_ext_hist")
    enable_account(session, resource_id)
    disable_account(session, resource_id)
    return user_id
