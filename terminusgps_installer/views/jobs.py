import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.forms import InstallJobCompletionForm, InstallJobCreationForm
from terminusgps_installer.models import Installer, InstallJob, WialonAsset


class InstallJobListView(LoginRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    context_object_name = "job_list"
    extra_context = {"title": "Install Jobs List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = InstallJob
    partial_template_name = "terminusgps_installer/jobs/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/jobs/list.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("asset", "account")
            .filter(installer__user=self.request.user)
        )
        if self.request.GET.get("completed"):
            qs = qs.filter(
                completed=True
                if self.request.GET.get("completed", "false") == "true"
                else False
            )
        return qs


class InstallJobCompleteView(LoginRequiredMixin, HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    context_object_name = "job"
    extra_context = {"title": "Complete Install Job"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/jobs/partials/_complete.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/jobs/complete.html"
    form_class = InstallJobCompletionForm
    success_url = reverse_lazy("installer:dashboard")

    def get_success_url(self, job: InstallJob | None = None) -> str:
        if job is not None:
            return reverse("installer:job complete success", kwargs={"pk": job.pk})
        return super().get_success_url()

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["job"] = self._get_job()
        return context

    def form_valid(
        self, form: InstallJobCompletionForm
    ) -> HttpResponse | HttpResponseRedirect:
        job = self._get_job()
        if job is None:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Couldn't find job with pk '%(pk)s'."),
                    code="invalid",
                    params={"pk": self.kwargs.get("pk")},
                ),
            )
            return self.form_invalid(form=form)
        job = self._complete_job(job)
        return HttpResponseRedirect(self.get_success_url(job))

    @staticmethod
    @transaction.atomic
    def _complete_job(job: InstallJob) -> InstallJob:
        print("Setting job as completed...")
        job.completed = True
        job.save()
        return job

    def _get_job(self) -> InstallJob | None:
        return (
            InstallJob.objects.select_related("asset").get(pk=self.kwargs["pk"])
            if self.kwargs.get("pk")
            else None
        )


class InstallJobCompleteSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Completed Install Job"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/jobs/partials/_complete_success.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/jobs/complete_success.html"
    model = InstallJob
    queryset = InstallJob.objects.select_related("asset")
    context_object_name = "job"


class InstallJobDetailView(LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    context_object_name = "job"
    extra_context = {"title": "Install Job Details"}
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

    @transaction.atomic
    def form_valid(
        self, form: InstallJobCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        imei_number: str = form.cleaned_data["imei_number"]
        with WialonSession() as session:
            unit = wialon_utils.get_unit_by_imei(imei=imei_number, session=session)
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
            asset = self.create_wialon_asset_commands(asset, session)
            job = InstallJob.objects.create(
                installer=Installer.objects.get(user=self.request.user),
                account=form.cleaned_data["account"],
                asset=asset,
            )
            return HttpResponseRedirect(job.get_absolute_url())

    @transaction.atomic
    def create_wialon_asset_commands(
        self, asset: WialonAsset, session: WialonSession
    ) -> WialonAsset:
        if asset.commands.count() == 0:
            asset.save(session)
        return asset

    @transaction.atomic
    def create_wialon_asset(self, unit: WialonUnit) -> WialonAsset:
        return WialonAsset.objects.create(
            id=unit.id, name=unit.name, imei=unit.imei_number
        )
