import functools

from django.http import HttpRequest, HttpResponse


def is_htmx_request(request: HttpRequest) -> bool:
    hx_request = request.headers.get("HX-Request", "false") == "true"
    hx_boosted = request.headers.get("HX-Boosted", "false") == "true"
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
