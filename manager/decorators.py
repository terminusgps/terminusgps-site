import functools
import logging

from django.conf import settings
from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse
from terminusgps.wialon.session import WialonSession

from .wialon import session_is_active

logger = logging.getLogger(__name__)


class HttpRequest(HttpRequestBase):
    template_name: str


def htmx_request(request: HttpRequest) -> bool:
    hx_request = bool(request.headers.get("HX-Request"))
    hx_boosted = bool(request.headers.get("HX-Boosted"))
    return hx_request and not hx_boosted


def htmx_template(template_name: str):
    def outer_wrapper(view_func):
        @functools.wraps(view_func)
        def inner_wrapper(
            request: HttpRequest, *args, **kwargs
        ) -> HttpResponse:
            if htmx_request(request):
                request.template_name = template_name + "#main"
            else:
                request.template_name = template_name
            return view_func(request, *args, **kwargs)

        return inner_wrapper

    return outer_wrapper


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
