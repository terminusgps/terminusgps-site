from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
)
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.vary import vary_on_headers

from terminusgps.decorators import htmx_template

from .forms import ContactForm


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/home.html")
def home_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@cache_control(max_age=300, private=True)
@require_GET
@htmx_template("terminusgps/navbar.html")
def navbar_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/contact.html")
def contact_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@never_cache
@require_http_methods(["GET", "POST"])
@htmx_template("terminusgps/contact_form.html")
def contact_form_view(request: HttpRequest) -> HttpResponse:
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_form_response = form.save(commit=True)
            contact_form_response.email_to_admins()
            return redirect("contact form success")
    return TemplateResponse(request, request.template_name, {"form": form})


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/contact_form_success.html")
def contact_form_success_view(request: HttpRequest) -> HttpResponse:
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


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/features.html")
def features_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps/faq.html")
def faq_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@require_GET
def source_code_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    url = "https://github.com/terminusgps/terminusgps-site/"
    return redirect(url, permanent=True)


@require_GET
def platform_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    url = "https://hosting.terminusgps.com/"
    return redirect(url, permanent=True)


@require_GET
def cameras_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    url = "https://camera.terminusgps.com/"
    return redirect(url, permanent=True)


@require_GET
def ios_app_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    url = "https://apps.apple.com/us/app/terminus-gps-mobile/id1419439009"
    return redirect(url, permanent=True)


@require_GET
def android_app_view(request: HttpRequest) -> HttpResponsePermanentRedirect:
    url = "https://play.google.com/store/apps/details?id=com.terminusgps.track&pcampaignid=web_share"
    return redirect(url, permanent=True)
