import functools

from django.http import HttpRequest, HttpResponse

from terminusgps.wialon import get_session


def is_htmx_request(request: HttpRequest) -> bool:
    hx_request = bool(request.headers.get("HX-Request"))
    hx_boosted = bool(request.headers.get("HX-Boosted"))
    return hx_request and not hx_boosted


def htmx_template(template_name: str):
    def outer_wrapper(view_func):
        @functools.wraps(view_func)
        def inner_wrapper(
            request: HttpRequest, *args, **kwargs
        ) -> HttpResponse:
            if is_htmx_request(request):
                request.template_name = template_name + "#main"
            else:
                request.template_name = template_name
            return view_func(request, *args, **kwargs)

        return inner_wrapper

    return outer_wrapper


def persistent_wialon_session(view_func=None):
    def outer_wrapper(view_func):
        @functools.wraps(view_func)
        def inner_wrapper(
            request: HttpRequest, *args, **kwargs
        ) -> HttpResponse:
            sid = request.session.pop("wialon_sid", None)
            session = get_session(sid=sid)
            request.session["wialon_sid"] = session.id
            return view_func(request, *args, **kwargs)

        return inner_wrapper

    if view_func is None:
        return outer_wrapper
    else:
        return outer_wrapper(view_func)
