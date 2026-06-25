import functools
from collections.abc import Sequence
from typing import Any

from django.conf import settings
from wialon.api import Wialon, WialonError

from .constants import CommandFlag, CommandLinkType


class WialonSession:
    def __init__(
        self,
        scheme: str = "https",
        host: str = "hst-api.wialon.com",
        port: int = 443,
        sid: str | None = None,
        token: str | None = None,
    ) -> None:
        self._wialon_api = Wialon(scheme=scheme, host=host, port=port, sid=sid)
        self._token = token or settings.WIALON_TOKEN
        self._uid = None
        self._gis_sid = None
        self._username = None

    def __str__(self) -> str:
        return f"WialonSession #{self.id}"

    def __repr__(self) -> str:
        return f"{self.__class__}(sid={self.id})"

    def __enter__(self) -> "WialonSession":
        if self.id is None:
            self.token_login(token=self._token, username=self._username)
        return self

    def __exit__(self, a, b, c) -> None:
        if self.id is not None:
            self.logout()

    def token_login(self, token: str, username: str | None = None) -> None:
        params = {"token": token, "flags": 0x3 if username else 0x1}
        if username is not None:
            params["operateAs"] = username
        response = self.wialon_api.token_login(**params)
        self.wialon_api.sid = response.get("eid")
        self._username = response.get("au")
        self._uid = response.get("user", {}).get("id")
        self._gis_sid = response.get("gis_sid")

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

    @property
    def gis_sid(self):
        return self._gis_sid


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
    :rtype: ~terminusgps.wialon.WialonSession

    """
    session = WialonSession(sid=sid)
    if session_is_active(session):
        return session
    else:
        session.token_login(token=settings.WIALON_TOKEN)
        return session


@functools.lru_cache(maxsize=300)
def get_unit_by_imei(
    session: WialonSession, imei: str, flags: int = 1
) -> dict:
    """
    Returns a Wialon unit dictionary by IMEI # (sys_unique_id).

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
    :param imei: An IMEI number.
    :type imei: str
    :param flags: Response flags. Default is ``1``.
    :type flags: int
    :raises wialon.api.WialonError: If anything went wrong calling the Wialon API.
    :returns: A Wialon unit dictionary.
    :rtype: dict

    """
    response = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": f"={imei}",
                "propType": "property",
                "sortType": "sys_name",
            },
            "from": 0,
            "to": 0,
            "force": 0,
            "flags": flags,
        }
    )
    if response["totalItemsCount"] != 1:
        raise WialonError(-1, f"Too many items returned for IMEI #: {imei}")
    return response["items"][0]


@functools.lru_cache(maxsize=300)
def get_unit_by_id(
    session: WialonSession, unit_id: int, flags: int = 1
) -> dict:
    """
    Returns a Wialon unit dictionary by id.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
    :param unit_id: A Wialon unit id.
    :type unit_id: int
    :param flags: Response flags. Default is ``1``.
    :type flags: int
    :raises wialon.api.WialonError: If anything went wrong calling the Wialon API.
    :returns: A Wialon unit dictionary.
    :rtype: dict

    """
    response = session.wialon_api.core_search_item(
        **{"id": unit_id, "flags": flags}
    )
    return response["item"]


@functools.lru_cache(maxsize=300)
def get_resource(
    session: WialonSession, resource_id: int, flags: int = 1
) -> dict:
    response = session.wialon_api.core_search_item(
        **{"id": resource_id, "flags": flags}
    )
    return response["item"]


@functools.lru_cache(maxsize=300)
def get_vin_info(session: WialonSession, vin: str) -> dict:
    """
    Returns VIN number info from Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
    :param vin: A VIN number.
    :type vin: str
    :returns: A dictionary of VIN number info.
    :rtype: dict

    """
    response = session.wialon_api.unit_get_vin_info(**{"vin": vin})
    return response["vin_lookup_result"]


@functools.lru_cache(maxsize=300)
def get_resource_choices(session: WialonSession) -> list[tuple]:
    """
    Returns a list of resources from Wialon as choice tuples.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
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
    :type session: ~terminusgps.wialon.WialonSession
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
    :type session: ~terminusgps.wialon.WialonSession
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
    :type session: ~terminusgps.wialon.WialonSession
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
    :type session: ~terminusgps.wialon.WialonSession
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
    :type session: ~terminusgps.wialon.WialonSession
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


@functools.lru_cache(maxsize=300)
def get_command_definition_data(
    session: WialonSession,
    unit_id: int,
    command_ids: Sequence[int] | None = None,
) -> list[dict]:
    """
    Returns definition data for all unit commmands.

    Returns command definition data only for ``command_ids`` if specified.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
    :param unit_id: A Wialon unit id.
    :type unit_id: int
    :param command_ids: Optional. A sequence of command ids.
    :type command_ids: ~collections.abc.Sequence[int] | None
    :returns: A list of command definition data dictionaries.
    :rtype: list[dict]

    """
    params: dict[str, Any] = {"itemId": unit_id}
    if command_ids is not None:
        params["col"] = command_ids
    return session.wialon_api.unit_get_command_definition_data(**params)


@functools.lru_cache(maxsize=300)
def get_command_name(
    session: WialonSession, unit_id: int, command_id: int
) -> str | None:
    """
    Returns the name of the Wialon command, if found.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
    :param unit_id: A Wialon unit id.
    :type unit_id: int
    :param command_id: A Wialon unit command id.
    :type command_id: int
    :returns: The command name, if found.
    :rtype: str | None

    """
    commands = get_command_definition_data(session, unit_id, (command_id,))
    if not commands or len(commands) > 1:
        return
    return commands[0]["n"]


def execute_command(
    session: WialonSession,
    unit_id: int,
    command_name: str,
    link_type: CommandLinkType = CommandLinkType.AUTO,
    param: str = "",
    timeout: int = 300,
    flags: CommandFlag = CommandFlag.USE_ANY,
) -> dict:
    """
    Executes a unit command by name.

    ATTENTION: This function only *queues* the command for execution, results from executing the command **must be retrieved separately**.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSession
    :param unit_id: A Wialon unit id.
    :type unit_id: int
    :param command_name: A Wialon unit command name.
    :type command_name: str
    :param link_type: Command link type. Default is :py:obj:`~terminusgps.constants.CommandLinkType.AUTO`.
    :type link_type: ~terminusgps.constants.CommandLinkType
    :param param: Additional command parameters. Default is ``""``.
    :type param: str
    :param timeout: Timeout in seconds. Default is ``300``.
    :type timeout: int
    :param flags: Flags for selecting a phone number to execute the command. Default is :py:obj:`~terminusgps.constants.CommandFlag.USE_ANY`.
    :type flags: ~terminusgps.constants.CommandFlag
    :returns: An empty dictionary.
    :rtype: dict

    """
    return session.wialon_api.unit_exec_cmd(
        **{
            "itemId": unit_id,
            "commandName": command_name,
            "linkType": link_type,
            "timeout": timeout,
            "flags": flags,
            "param": param,
        }
    )


def update_vin(session: WialonSession, unit_id: int, vin: str) -> None:
    """
    Updates a unit's VIN number in Wialon.

    :param session: A valid Wialon API session.
    :type session: ~terminusgps.wialon.WialonSesison
    :param unit_id: A Wialon unit id.
    :type unit_id: int
    :param vin: A VIN number.
    :type vin: str
    :returns: Nothing.
    :rtype: None

    """
    session.wialon_api.item_update_profile_field(
        **{"itemId": unit_id, "n": "vin", "v": vin}
    )
