import typing

from django import forms
from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, UpdateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.items.unit import WialonUnit
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.forms import WialonAssetCommandExecutionForm
from terminusgps_installer.models import WialonAsset, WialonAssetCommand
from terminusgps_installer.views.mixins import InstallerRequiredMixin


class WialonAssetDetailView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {"title": "Asset Details"}
    model = WialonAsset
    partial_template_name = (
        "terminusgps_installer/assets/partials/_detail.html"
    )
    pk_url_kwarg = "asset_pk"
    template_name = "terminusgps_installer/assets/detail.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self._asset_commands_need_wialon_sync():
            with WialonSession() as session:
                asset = self.get_object()
                asset.wialon_sync(session)
        return super().get(request, *args, **kwargs)

    def _asset_commands_need_wialon_sync(self) -> bool:
        return self.get_object().commands.count() == 0


class WialonAssetUpdateView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {
        "title": "Update Asset",
        "subtitle": "Update Wialon asset data",
    }
    fields = ["name", "imei", "vin"]
    http_method_names = ["get", "post"]
    model = WialonAsset
    partial_template_name = (
        "terminusgps_installer/assets/partials/_update.html"
    )
    pk_url_kwarg = "asset_pk"
    template_name = "terminusgps_installer/assets/update.html"

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form()
        for field in form.fields:
            form.fields[field].widget.attrs.update(
                {"class": settings.DEFAULT_FIELD_CLASS}
            )
        form.fields["name"].label = "Name"
        form.fields["vin"].label = "VIN #"
        form.fields["imei"].label = "IMEI #"
        return form

    def form_valid(
        self, form: forms.ModelForm
    ) -> HttpResponse | HttpResponseRedirect:
        with WialonSession() as session:
            new_name = form.cleaned_data["name"]
            asset = self.get_object()
            unit = WialonUnit(id=asset.pk, session=session)
            if asset.name != new_name:
                unit.rename(new_name)
        return super().form_valid(form=form)


class WialonAssetPositionView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Asset Position"}
    model = WialonAsset
    partial_template_name = (
        "terminusgps_installer/assets/partials/_position.html"
    )
    pk_url_kwarg = "asset_pk"
    template_name = "terminusgps_installer/assets/position.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        with WialonSession() as session:
            unit = WialonUnit(id=self.kwargs["asset_pk"], session=session)
            context["pos"] = unit.get_position()
        return context


class WialonAssetCommandListView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "command_list"
    extra_context = {"title": "Command"}
    http_method_names = ["get"]
    model = WialonAssetCommand
    ordering = "name"
    paginate_by = 4
    partial_template_name = (
        "terminusgps_installer/assets/partials/_command_list.html"
    )
    queryset = WialonAssetCommand.objects.all()
    template_name = "terminusgps_installer/assets/command_list.html"

    def get_queryset(self) -> QuerySet[WialonAssetCommand, WialonAssetCommand]:
        return (
            WialonAsset.objects.get(pk=self.kwargs["asset_pk"])
            .commands.select_related("asset")
            .order_by(self.get_ordering())
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["title"] = f"{self.get_queryset().first().asset.name} Commands"
        return context


class WialonAssetCommandDetailView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "command"
    extra_context = {"title": "Asset Command"}
    http_method_names = ["get"]
    model = WialonAssetCommand
    partial_template_name = (
        "terminusgps_installer/assets/partials/_command_detail.html"
    )
    pk_url_kwarg = "cmd_pk"
    queryset = WialonAssetCommand.objects.all()
    template_name = "terminusgps_installer/assets/command_detail.html"

    def get_object(self) -> WialonAssetCommand:
        return (
            WialonAsset.objects.get(pk=self.kwargs["asset_pk"])
            .commands.select_related("asset")
            .get(pk=self.kwargs["cmd_pk"])
        )


class WialonAssetCommandExecuteView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "command"
    extra_context = {"title": "Execute Command"}
    form_class = WialonAssetCommandExecutionForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_installer/assets/partials/_command_execute.html"
    )
    template_name = "terminusgps_installer/assets/command_execute.html"

    def form_valid(
        self, form: WialonAssetCommandExecutionForm
    ) -> HttpResponse | HttpResponseRedirect:
        with WialonSession() as session:
            command: WialonAssetCommand = self.get_object()
            command.execute(session, link_type=form.cleaned_data["link_type"])
        return super().form_valid(form=form)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["command"] = self.get_object()
        return context

    def get_success_url(self) -> str:
        return reverse(
            "installer:command execute success",
            kwargs={
                "asset_pk": self.kwargs["asset_pk"],
                "cmd_pk": self.kwargs["cmd_pk"],
            },
        )

    def get_object(self) -> WialonAssetCommand:
        return (
            WialonAsset.objects.get(pk=self.kwargs["asset_pk"])
            .commands.select_related("asset")
            .get(pk=self.kwargs["cmd_pk"])
        )


class WialonAssetCommandExecuteSuccessView(
    HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "command"
    extra_context = {"title": "Command Executed"}
    http_method_names = ["get"]
    model = WialonAssetCommand
    partial_template_name = (
        "terminusgps_installer/assets/partials/_command_execute_success.html"
    )
    pk_url_kwarg = "cmd_pk"
    queryset = WialonAssetCommand.objects.all()
    template_name = "terminusgps_installer/assets/command_execute_success.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        with WialonSession() as session:
            unit = WialonUnit(id=self.get_object().asset.pk, session=session)
            context["last_msg"] = unit.get_command_messages(
                timezone.now()
            ).get("messages")[0]
        return context

    def get_object(self) -> WialonAssetCommand:
        return (
            WialonAsset.objects.get(pk=self.kwargs["asset_pk"])
            .commands.select_related("asset")
            .get(pk=self.kwargs["cmd_pk"])
        )
