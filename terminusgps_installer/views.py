import logging

import wialon.api
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, never_cache
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.vary import vary_on_headers
from formset.views import FormCollectionView

from terminusgps.decorators import htmx_template
from terminusgps.wialon import get_session

from .forms import CommandExecutionForm, InstallJobCollection
from .models import Employee, InstallJob, WialonUnit

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


@method_decorator(cache_control(max_age=300), name="dispatch")
@method_decorator(login_required, name="dispatch")
class NewJobFormView(FormCollectionView):
    collection_class = InstallJobCollection
    template_name = "installer/new_job.html"
    success_url = reverse_lazy("installer:job list")

    def form_collection_valid(self, form_collection):
        job = InstallJob.objects.create(
            employee=form_collection.cleaned_data["job"]["employee"],
            company=form_collection.cleaned_data["job"]["company"],
        )
        for data in form_collection.cleaned_data["units"]:
            unit = WialonUnit()
            unit.job = job
            unit.imei = data["unit"]["imei"]
            unit.vin = data["unit"].get("vin", "")
            unit.plate = data["unit"].get("plate", "")
            unit.mileage = data["unit"].get("mileage", 0)
            unit.save()
            unit.get_wialon_unit_name_and_save()
            unit.refresh_locator_url_and_save()
        return super().form_collection_valid(form_collection)


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
    unit_qs = job.units.filter()
    context = {"job": job, "units": unit_qs.with_wialon_commands()}
    return TemplateResponse(request, request.template_name, context)


@login_required
@never_cache
@htmx_template("installer/command_executed.html")
@require_POST
def execute_command_view(request: HttpRequest, unit_pk: int) -> HttpResponse:
    unit = get_object_or_404(WialonUnit, pk=unit_pk)
    form = CommandExecutionForm(request.POST)
    if not form.is_valid():
        command = None
        queued = False
    else:
        command = form.cleaned_data["command_name"]
        try:
            unit.execute_wialon_command(command)
        except wialon.api.WialonError as error:
            logger.error(error)
            queued = False
        else:
            queued = True
    return TemplateResponse(
        request, request.template_name, {"command": command, "queued": queued}
    )


@login_required
@cache_control(max_age=300)
@htmx_template("installer/command_list.html")
@require_GET
def command_list_view(request: HttpRequest, unit_pk: int) -> HttpResponse:
    session = get_session(sid=None)
    unit = get_object_or_404(WialonUnit, pk=unit_pk)
    try:
        commands = unit.get_wialon_commands(session)
    except wialon.api.WialonError as error:
        logger.error(error)
        commands = []
    return TemplateResponse(
        request, request.template_name, {"commands": commands, "unit": unit}
    )
