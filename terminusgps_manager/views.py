from django.contrib.auth.decorators import login_required
from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.vary import vary_on_headers

from src.decorators import htmx_template

from .authorizenet import get_hosted_profile_page_url
from .forms import ContactForm
from .models import TerminusProfile


# For type checkers
class HttpRequest(HttpRequestBase):
    template_name: str


@vary_on_headers("HX-Request")
@cache_control(private=True, max_age=300)
@htmx_template("terminusgps_manager/dashboard.html")
@require_GET
@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    profile, created = TerminusProfile.objects.get_or_create(user=request.user)
    context = {"profile": profile, "created": created}
    return TemplateResponse(request, request.template_name, context)


@never_cache
@htmx_template("terminusgps_manager/hosted_profile.html")
@require_http_methods(["GET", "POST"])
@login_required
def authorizenet_hosted_profile_view(request: HttpRequest) -> HttpResponse:
    profile = get_object_or_404(TerminusProfile, user=request.user)
    if not profile.authorizenet_customer_profile_id:
        ...
    token = None
    context = {"token": token, "url": get_hosted_profile_page_url()}
    return TemplateResponse(request, request.template_name, context)


@never_cache
@require_http_methods(["GET", "POST"])
@htmx_template("terminusgps_manager/contact_form.html")
def contact_form_view(request: HttpRequest) -> HttpResponse:
    form = ContactForm()
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("manager:contact form success")
    context = {"form": form}
    return TemplateResponse(request, request.template_name, context)


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@require_GET
@htmx_template("terminusgps_manager/contact_form_success.html")
def contact_form_success_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)
