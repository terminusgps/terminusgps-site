import logging

import wialon.api
from terminusgps.wialon.session import WialonAPIError, WialonSession

from .models import TerminusProfile

logger = logging.getLogger(__name__)


def get_session(sid: str | None = None) -> WialonSession:
    return WialonSession(sid=sid)


def session_is_active(sid: str | None = None) -> bool:
    session = WialonSession(sid=sid)
    try:
        session.wialon_api.avl_evts()
    except wialon.api.WialonError as error:
        if error._code == 1:
            return False
        raise
    else:
        return True


def get_user(
    profile: TerminusProfile, flags: int = 1, sid: str | None = None
) -> dict:
    if not profile.wialon_user_id:
        return {}
    wialon_session = get_session(sid)
    wialon_params = {"id": profile.wialon_user_id, "flags": flags}
    try:
        wialon_response = wialon_session.wialon_api.core_search_item(
            **wialon_params
        )
    except WialonAPIError as error:
        logger.error(error)
        return {}
    else:
        return wialon_response["item"]
