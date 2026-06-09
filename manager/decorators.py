import functools

from django.conf import settings
from terminusgps.wialon.session import WialonSession

from .wialon import session_is_active


def persistent_wialon_session(view_func=None):
    def outer_wrapper(view_func):
        @functools.wraps(view_func)
        def inner_wrapper(request, *args, **kwargs):
            sid = request.session.pop("wialon_sid", None)
            if session_is_active(sid):
                request.session["wialon_sid"] = sid
            else:
                session = WialonSession(sid=None)
                session.token_login(token=settings.WIALON_TOKEN)
                request.session["wialon_sid"] = session.id
            return view_func(request, *args, **kwargs)

        return inner_wrapper

    if view_func is None:
        return outer_wrapper
    else:
        return outer_wrapper(view_func)
