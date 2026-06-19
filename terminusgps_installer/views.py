import logging

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.http import HttpRequest as HttpRequestBase
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.vary import vary_on_headers

from terminusgps.decorators import htmx_template

from .forms import NewInstallJobForm
from .models import Installer, InstallJob

logger = logging.getLogger(__name__)


class HttpRequest(HttpRequestBase):
    template_name: str


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300, private=True)
@htmx_template("installer/start_new_job.html")
@require_GET
def start_new_job_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@htmx_template("installer/select_resource.html")
@require_GET
def select_resource_view(request: HttpRequest) -> HttpResponse:
    # session = wialon.get_session(sid=None)
    # try:
    #     choices = wialon.get_resource_choices(session)
    # except WialonAPIError as error:
    #     logger.error(error)
    #     choices = []
    return TemplateResponse(request, request.template_name, {"choices": []})


@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@htmx_template("installer/vin_info.html")
@require_GET
def vin_info_view(request: HttpRequest) -> HttpResponse:
    vin = request.GET.get("vin")
    if not vin:
        raise Http404()
    # session = wialon.get_session(sid=None)
    # try:
    #     vin_info = wialon.get_vin_info(session, str(vin))
    # except WialonAPIError as error:
    #     logger.error(error)
    #     vin_info = {"error": True, "message": error}
    return TemplateResponse(
        request,
        request.template_name,
        {"vin_info": {"error": True, "message": "TODO"}},
    )


@login_required
@vary_on_headers("HX-Request")
@never_cache
@htmx_template("installer/new_job_form.html")
@require_http_methods(["GET", "POST"])
def new_job_form_view(request: HttpRequest) -> HttpResponse:
    try:
        installer = Installer.objects.get(user=request.user)
    except Installer.DoesNotExist:
        installer = None
    initial = {"mileage": 0, "installer": installer}
    form = NewInstallJobForm(initial=initial)
    if request.method == "POST":
        form = NewInstallJobForm(request.POST, initial=initial)
        if form.is_valid():
            form.save(commit=True)
            return redirect("installer:incomplete jobs")
    return TemplateResponse(request, request.template_name, {"form": form})


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300, private=True)
@htmx_template("installer/new_job_success.html")
@require_GET
def new_job_success_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300, private=True)
@htmx_template("installer/incomplete_jobs.html")
@require_GET
def incomplete_jobs_view(request: HttpRequest) -> HttpResponse:
    qs = InstallJob.objects.all_incomplete_jobs().filter(
        installer__user=request.user
    )
    return TemplateResponse(
        request, request.template_name, {"object_list": qs}
    )
