import functools

from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse


# For type checkers
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
