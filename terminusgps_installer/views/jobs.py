import typing

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items.unit import WialonUnit
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.forms import (
    InstallJobCompletionForm,
    InstallJobCreationForm,
)
from terminusgps_installer.models import (
    Installer,
    InstallJob,
    WialonAccount,
    WialonAsset,
)
from terminusgps_installer.views.mixins import InstallerRequiredMixin


class InstallJobListView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "job_list"
    extra_context = {"title": "Install Jobs List"}
    http_method_names = ["get"]
    model = InstallJob
    partial_template_name = "terminusgps_installer/jobs/partials/_list.html"
    template_name = "terminusgps_installer/jobs/list.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if self.request.GET.get("completed"):
            if self.request.GET["completed"] == "true":
                context["title"] = "Completed Jobs"
                context["subtitle"] = "Review your past jobs"
            elif self.request.GET["completed"] == "false":
                context["title"] = "On-going Jobs"
                context["subtitle"] = "Complete your on-going jobs"
        return context

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


class InstallJobCompleteView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "job"
    extra_context = {"title": "Complete Install Job"}
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_installer/jobs/partials/_complete.html"
    )
    template_name = "terminusgps_installer/jobs/complete.html"
    form_class = InstallJobCompletionForm

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["job"] = self.get_object()
        return context

    def form_valid(
        self, form: InstallJobCompletionForm
    ) -> HttpResponse | HttpResponseRedirect:
        job = self.get_object()
        job.completed = True
        job.save()
        return HttpResponseRedirect(
            reverse("installer:job complete", kwargs={"job_pk": job.pk})
        )

    def get_object(self) -> InstallJob:
        return InstallJob.objects.get(pk=self.kwargs["job_pk"])


class InstallJobCompleteSuccessView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Completed Install Job"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_installer/jobs/partials/_complete_success.html"
    )
    template_name = "terminusgps_installer/jobs/complete_success.html"
    model = InstallJob
    queryset = InstallJob.objects.select_related("asset", "account")
    context_object_name = "job"
    pk_url_kwarg = "job_pk"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        with WialonSession() as session:
            unit = WialonUnit(id=self.get_object().asset.pk, session=session)
        return super().get(request, *args, **kwargs)


class InstallJobDetailView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "job"
    extra_context = {"title": "Install Job Details"}
    http_method_names = ["get"]
    model = InstallJob
    partial_template_name = "terminusgps_installer/jobs/partials/_detail.html"
    pk_url_kwarg = "job_pk"
    template_name = "terminusgps_installer/jobs/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["title"] = f"Install Job #{self.get_object().pk}"
        return context

    def get_queryset(self):
        return super().get_queryset().select_related("asset", "account")


class InstallJobCreateView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "job"
    extra_context = {
        "title": "Create Install Job",
        "subtitle": "Setting up your new install job",
    }
    form_class = InstallJobCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_installer/jobs/partials/_create.html"
    template_name = "terminusgps_installer/jobs/create.html"

    def get_form(self, form_class=None) -> InstallJobCreationForm:
        """
        Sets possible account choices on the form based on the installer.

        :returns: An install job creation form.
        :rtype: :py:obj:`~terminusgps_installer.forms.InstallJobCreationForm`

        """
        try:
            form = super().get_form(form_class=form_class)
            installer = Installer.objects.get(user=self.request.user)
            form.fields["account"].queryset = installer.accounts.all()
            return form
        except Installer.DoesNotExist:
            return form

    @transaction.atomic
    def form_valid(
        self, form: InstallJobCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Creates an install job and associated objects based on the form before redirecting the client to the new install job's detail view.

        If the provided ``imei_number`` from the form is not associated with a Wialon unit, renders the form with errors.

        :param form: An install job creation form.
        :type form: :py:obj:`~terminusgps_installer.forms.InstallJobCreationForm`
        :returns: An http response.
        :rtype: :py:obj:`~django.http.HttpResponse` | :py:obj:`~django.http.HttpResponseRedirect`

        """
        imei_number: str = form.cleaned_data["imei_number"]
        account: WialonAccount = form.cleaned_data["account"]

        with WialonSession() as session:
            unit = wialon_utils.get_unit_by_imei(
                imei=imei_number, session=session
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

            asset = WialonAsset.objects.create(
                id=unit.id, name=unit.name, imei=unit.imei_number
            )
            job = InstallJob.objects.create(
                installer=Installer.objects.get(user=self.request.user),
                asset=asset,
                account=account,
            )
            return HttpResponseRedirect(job.get_absolute_url())
