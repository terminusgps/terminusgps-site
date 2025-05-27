import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSessionManager

from terminusgps_installer.forms import InstallJobCreationForm
from terminusgps_installer.models import (
    Installer,
    InstallJob,
    WialonAccount,
    WialonAsset,
)


class InstallJobListView(LoginRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    context_object_name = "job_list"
    extra_context = {"title": "Install Jobs List", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = InstallJob
    partial_template_name = "terminusgps_installer/jobs/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/jobs/list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("installer__user", "asset", "account")
            .filter(installer__user=self.request.user)
        )


class InstallJobDetailView(LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    context_object_name = "job"
    extra_context = {"title": "Install Job Details", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = InstallJob
    partial_template_name = "terminusgps_installer/jobs/partials/_detail.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/jobs/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["title"] = f"Install Job #{self.kwargs['pk']}"
        return context

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("installer__user", "asset", "account")
            .filter(installer__user=self.request.user)
        )


class InstallJobCreateView(LoginRequiredMixin, HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    context_object_name = "job"
    extra_context = {"title": "Create Install Job", "class": "flex flex-col gap-8"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/jobs/create.html"
    partial_template_name = "terminusgps_installer/jobs/partials/_create.html"
    form_class = InstallJobCreationForm

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.session_manager = WialonSessionManager(token=settings.WIALON_TOKEN)

    @transaction.atomic
    def form_valid(
        self, form: InstallJobCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        imei_number: str = form.cleaned_data["imei_number"]
        unit: WialonUnit | None = wialon_utils.get_unit_by_imei(
            imei=imei_number, session=self.session_manager.get_session(sid=None)
        )
        if unit is None:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "Whoops! No device with IMEI #%(imei_number)s found in Wialon. It may not exist."
                    ),
                    code="invalid",
                    params={"imei_number": imei_number},
                ),
            )
            return self.form_invalid(form=form)

        asset = self.create_wialon_asset(unit)
        job = self.create_install_job(asset, form.cleaned_data["account"])
        return HttpResponseRedirect(job.get_absolute_url())

    @transaction.atomic
    def create_wialon_asset(self, unit: WialonUnit) -> WialonAsset:
        return WialonAsset.objects.create(id=unit.id, name=unit.name)

    @transaction.atomic
    def create_install_job(
        self, asset: WialonAsset, account: WialonAccount
    ) -> InstallJob:
        installer = Installer.objects.get(user=self.request.user)
        return InstallJob.objects.create(
            installer=installer, account=account, asset=asset
        )
