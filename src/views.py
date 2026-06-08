from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import redirect_to_login
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
)
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods


@require_http_methods(["GET", "POST"])
def register_view(request: HttpRequest) -> HttpResponse:
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect_to_login(
                next=reverse("home"), login_url=reverse("login")
            )
    return TemplateResponse(
        request, "registration/register.html", {"form": form}
    )


@require_GET
def home_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "terminusgps/home.html")


@require_GET
def contact_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "terminusgps/contact.html")


@require_GET
def about_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "terminusgps/about.html")


@require_GET
def terms_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "terminusgps/terms.html")


@require_GET
def privacy_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, "terminusgps/privacy.html")


@require_GET
def source_code_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    return redirect(
        "https://github.com/terminusgps/terminusgps-site/", permanent=True
    )
