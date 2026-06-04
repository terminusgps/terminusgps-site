from django.http import HttpRequest, HttpResponsePermanentRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse


def home_view(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "terminusgps/home.html")


def contact_view(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "terminusgps/contact.html")


def about_view(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "terminusgps/about.html")


def terms_view(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "terminusgps/terms.html")


def privacy_view(request: HttpRequest) -> TemplateResponse:
    return TemplateResponse(request, "terminusgps/privacy.html")


def source_code_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    return redirect(
        "https://github.com/terminusgps/terminusgps-site/", permanent=True
    )
