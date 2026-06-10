import functools

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.vary import vary_on_headers


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


@never_cache
@require_http_methods(["GET", "POST"])
@htmx_template("registration/register.html")
def register_view(request: HttpRequest) -> HttpResponse:
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect_to_login(
                next=reverse("home"), login_url=reverse("login")
            )
    return TemplateResponse(request, request.template_name, {"form": form})


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/home.html")
def home_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/contact.html")
def contact_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/about.html")
def about_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/terms.html")
def terms_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/privacy.html")
def privacy_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@require_GET
def source_code_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    url = "https://github.com/terminusgps/terminusgps-site/"
    return redirect(to=url, permanent=True)
