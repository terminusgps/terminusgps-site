import logging

import wialon.api
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.vary import vary_on_headers

from terminusgps.decorators import htmx_template
from terminusgps.wialon import (
    get_resource_choices,
    get_session,
    get_unit_by_imei,
)

from .forms import NewInstallJobForm
from .models import Employee, InstallJob

logger = logging.getLogger(__name__)


class HttpRequest(HttpRequestBase):
    template_name: str


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@htmx_template("installer/home.html")
@require_GET
def home_view(request: HttpRequest) -> HttpResponse:
    return TemplateResponse(request, request.template_name)


@login_required
@vary_on_headers("HX-Request")
@never_cache
@htmx_template("installer/new_job_form.html")
@require_http_methods(["GET", "POST"])
def new_job_form_view(request: HttpRequest) -> HttpResponse:
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        employee = None
    initial = {"employee": employee}
    form = NewInstallJobForm(initial=initial)
    if request.method == "POST":
        form = NewInstallJobForm(request.POST, initial=initial)
        if form.is_valid():
            job = form.save(commit=True)
            return redirect("installer:job details", job_pk=job.pk)
    return TemplateResponse(request, request.template_name, {"form": form})


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@htmx_template("installer/job_list.html")
@require_GET
def job_list_view(request: HttpRequest) -> HttpResponse:
    employee = get_object_or_404(Employee, user=request.user)
    jobs_qs = InstallJob.objects.all_not_done_jobs().filter(employee=employee)
    context = {"jobs_list": jobs_qs.order_by("crt_date")}
    return TemplateResponse(request, request.template_name, context)


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@htmx_template("installer/job_details.html")
@require_GET
def job_details_view(request: HttpRequest, job_pk: int) -> HttpResponse:
    job = get_object_or_404(InstallJob, pk=job_pk)
    session = get_session()
    try:
        unit = get_unit_by_imei(session, job.imei, flags=513)
    except wialon.api.WialonError as error:
        logger.error(error)
        unit = None
    context = {"job": job, "unit": unit}
    return TemplateResponse(request, request.template_name, context)


@login_required
@vary_on_headers("HX-Request")
@cache_control(max_age=300)
@htmx_template("installer/select_resource.html")
@require_GET
def select_resource_view(request: HttpRequest) -> HttpResponse:
    session = get_session(sid=None)
    try:
        choices = get_resource_choices(session)
    except wialon.api.WialonError as error:
        logger.error(error)
        choices = []
    context = {"choices": choices}
    return TemplateResponse(request, request.template_name, context)
