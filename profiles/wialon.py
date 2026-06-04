import logging

from terminusgps.wialon.session import WialonSession

logger = logging.getLogger(__name__)


def get_session(
    wialon_sid: str, wialon_username: str | None = None
) -> WialonSession:
    return (
        WialonSession(sid=wialon_sid, username=wialon_username)
        if wialon_username
        else WialonSession(sid=wialon_sid)
    )
