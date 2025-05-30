import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSession

from terminusgps_installer.forms import WialonAssetCommandExecutionForm
from terminusgps_installer.models import WialonAsset, WialonAssetCommand


class WialonAssetDetailView(LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {"title": "Asset Details", "class": "flex flex-col gap-8"}
    login_url = reverse_lazy("login")
    model = WialonAsset
    partial_template_name = "terminusgps_installer/assets/partials/_detail.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/detail.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        asset = self.get_object()
        if asset.commands.count() == 0:
            with WialonSession() as session:
                asset.wialon_sync(session)
        return super().get(request, *args, **kwargs)


class WialonAssetPositionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Asset Position"}
    login_url = reverse_lazy("login")
    model = WialonAsset
    partial_template_name = "terminusgps_installer/assets/partials/_position.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/position.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        with WialonSession() as session:
            unit = WialonUnit(id=self.kwargs["pk"], session=session)
            context["pos"] = unit.get_position()
        return context


class WialonAssetMessagesView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Asset Messages"}
    login_url = reverse_lazy("login")
    model = WialonAsset
    partial_template_name = "terminusgps_installer/assets/partials/_messages.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/messages.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        return context


class WialonAssetCommandListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "command_list"
    extra_context = {"title": "Command"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = WialonAssetCommand
    queryset = WialonAssetCommand.objects.none()
    partial_template_name = "terminusgps_installer/assets/partials/_command_list.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/command_list.html"
    paginate_by = 4
    ordering = "name"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not kwargs.get("asset_pk"):
            return HttpResponse(status=406)
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        asset: WialonAsset | None = self._get_asset()
        return (
            asset.commands.all().order_by(self.get_ordering())
            if asset is not None
            else qs
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        asset = self._get_asset()
        if asset is not None:
            context["title"] = f"{asset.name} Commands"
            context["asset"] = asset
        return context

    def _get_asset(self) -> WialonAsset | None:
        if self.kwargs.get("asset_pk"):
            return WialonAsset.objects.get(pk=self.kwargs["asset_pk"])


class WialonAssetCommandDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {
        "title": "Asset Command",
        "class": "flex flex-col md:flex-row items-center justify-between gap-2 rounded border p-2 bg-gray-200 dark:bg-gray-800 drop-shadow",
    }
    context_object_name = "command"
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = WialonAssetCommand
    partial_template_name = "terminusgps_installer/assets/partials/_command_detail.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/command_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["asset"] = self._get_asset()
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not kwargs.get("asset_pk"):
            return HttpResponse(status=406)
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        asset = self._get_asset()
        if asset is not None:
            return asset.commands.all()
        return WialonAssetCommand.objects.none()

    def _get_asset(self) -> WialonAsset | None:
        if self.kwargs.get("asset_pk"):
            return WialonAsset.objects.get(pk=self.kwargs["asset_pk"])


class WialonAssetCommandExecuteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Execute Command"}
    context_object_name = "command"
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_installer/assets/partials/_command_execute.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/command_execute.html"
    form_class = WialonAssetCommandExecutionForm

    def get_success_url(self) -> str:
        return reverse(
            "installer:command execute success",
            kwargs={"asset_pk": self.kwargs["asset_pk"], "pk": self.kwargs["pk"]},
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["command"] = self._get_command()
        return context

    def form_valid(
        self, form: WialonAssetCommandExecutionForm
    ) -> HttpResponse | HttpResponseRedirect:
        with WialonSession() as session:
            link_type: str = form.cleaned_data["link_type"]
            command: WialonAssetCommand | None = self._get_command()
            if command is None:
                form.add_error(
                    None,
                    ValidationError(_("Whoops! Command not found."), code="invalid"),
                )
                return self.form_invalid(form=form)

            command.execute(session, link_type=link_type)
            return super().form_valid(form=form)

    def _get_command(self) -> WialonAssetCommand | None:
        if self.kwargs.get("pk"):
            return self._get_asset().commands.get(pk=self.kwargs["pk"])

    def _get_asset(self) -> WialonAsset | None:
        if self.kwargs.get("asset_pk"):
            return WialonAsset.objects.get(pk=self.kwargs["asset_pk"])


class WialonAssetCommandExecuteSuccessView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    extra_context = {"title": "Command Executed", "class": "flex flex-col gap-4 p-4"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_installer/assets/partials/_command_execute_success.html"
    )
    template_name = "terminusgps_installer/assets/command_execute_success.html"
    model = WialonAssetCommand
    queryset = WialonAssetCommand.objects.all()

    def get_queryset(self) -> QuerySet:
        asset: WialonAsset | None = self._get_asset()
        return asset.commands.all() if asset is not None else WialonAsset.objects.none()

    def _get_command(self) -> WialonAssetCommand | None:
        if self._get_asset() and self.kwargs.get("pk"):
            return self._get_asset().commands.get(pk=self.kwargs["pk"])

    def _get_asset(self) -> WialonAsset | None:
        if self.kwargs.get("asset_pk"):
            return WialonAsset.objects.get(pk=self.kwargs["asset_pk"])

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["command"] = self._get_command()
        return context
