import logging

import wialon.api
from terminusgps.wialon.session import WialonSession

logger = logging.getLogger(__name__)


def get_session(sid: str | None = None) -> WialonSession:
    """
    Resumes and returns a Wialon session by session id.

    If `sid` wasn't provided or was invalid, start a new session then return it.

    :param sid: A Wialon API session id.
    :type sid: str | None
    :returns: A valid Wialon API session.
    :rtype: ~terminusgps.wialon.session.WialonSession

    """
    return WialonSession(sid=sid)


def session_is_active(sid: str | None = None) -> bool:
    """
    Returns whether a Wialon session is active by session id.

    :param sid: A Wialon API session id.
    :type sid: str | None
    :returns: Whether the session is active.
    :rtype: bool

    """
    session = get_session(sid=sid)
    try:
        session.wialon_api.avl_evts()
    except wialon.api.WialonError as error:
        if error._code == 1:
            return False
        raise
    else:
        return True


# Create resource
# Create super user
# Create account
# Create end-user
# Assign permissions to end-user


def create_resource(
    session: WialonSession,
    creator_id: int,
    name: str,
    flags: int = 1,
    skip_creator_check: bool = True,
) -> int:
    response = session.wialon_api.core_create_resource(
        **{
            "creatorId": creator_id,
            "name": name,
            "dataFlags": flags,
            "skipCreatorCheck": int(skip_creator_check),
        }
    )
    return int(response["item"]["id"])


def create_account(
    session: WialonSession, resource_id: int, plan: str
) -> None:
    session.wialon_api.account_create_account(
        **{"itemId": resource_id, "plan": plan}
    )
