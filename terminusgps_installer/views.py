import logging

import wialon.api
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)
from django.views.decorators.vary import vary_on_headers

from terminusgps.decorators import htmx_template
from terminusgps.wialon import (
    execute_command,
    get_resource_choices,
    get_session,
    get_unit_by_id,
    get_unit_by_imei,
)

from .forms import (
    CommandExecutionForm,
    NewInstallJobForm,
    UpdateInstallJobForm,
)
from .models import Employee, InstallJob
from .tasks import send_job_created_email

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
            send_job_created_email.enqueue(job.pk)
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
    if not job.locator_url:
        job.refresh_locator_url()
    session = get_session()
    try:
        unit = get_unit_by_imei(session, job.imei, flags=513)
    except wialon.api.WialonError as error:
        logger.error(error)
        unit = None
    context = {"job": job, "unit": unit}
    return TemplateResponse(request, request.template_name, context)


@login_required
@require_http_methods(["GET", "POST"])
@never_cache
@htmx_template("installer/job_update.html")
def job_update_view(request: HttpRequest, job_pk: int) -> HttpResponse:
    form = UpdateInstallJobForm(request.POST)
    if form.is_valid():
        form.save(commit=True)
        return redirect("installer:job details", job_pk=job_pk)
    else:
        return TemplateResponse(request, request.template_name, {"form": form})


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


@login_required
@never_cache
@htmx_template("installer/command_executed.html")
@require_POST
def execute_command_view(request: HttpRequest, unit_id: int) -> HttpResponse:
    form = CommandExecutionForm(request.POST)
    if not form.is_valid():
        context = {"command": None, "queued": False}
        return TemplateResponse(request, request.template_name, context)
    else:
        command = form.cleaned_data["command_name"]
        session = get_session(sid=None)
        try:
            execute_command(session, unit_id, command)
        except wialon.api.WialonError as error:
            logger.error(error)
            queued = False
        else:
            queued = True
        context = {"command": command, "queued": queued}
        return TemplateResponse(request, request.template_name, context)


@login_required
@cache_control(max_age=300)
@htmx_template("installer/command_list.html")
@require_GET
def command_list_view(request: HttpRequest, unit_id: int) -> HttpResponse:
    session = get_session(sid=None)
    try:
        response = get_unit_by_id(session, unit_id, flags=512)
    except wialon.api.WialonError as error:
        logger.error(error)
        commands = []
    else:
        commands = response["cmds"]
    context = {"commands": commands, "unit_id": unit_id}
    return TemplateResponse(request, request.template_name, context)
