import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, UpdateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSession, WialonSessionManager

from terminusgps_installer.forms import WialonAssetCommandExecutionForm
from terminusgps_installer.models import WialonAsset, WialonAssetCommand


class WialonAssetDetailView(LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    extra_context = {"title": "Detail Asset", "class": "flex flex-col gap-4"}
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/assets/partials/_detail.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/detail.html"
    model = WialonAsset
    context_object_name = "asset"


class WialonAssetUpdateView(LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView):
    content_type = "text/html"
    extra_context = {"title": "Update Asset", "class": "flex flex-col gap-8"}
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/assets/partials/_update.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/update.html"
    model = WialonAsset
    context_object_name = "asset"


class WialonAssetPositionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Asset Position", "class": "flex flex-col gap-8"}
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/assets/partials/_position.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/position.html"
    model = WialonAsset

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.session_manager = WialonSessionManager(token=settings.WIALON_TOKEN)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["pos"] = self.wialon_get_unit_position(
            session=self.session_manager.get_session()
        )
        context["map_url"] = self.wialon_generate_map_url(
            session=self.session_manager.get_session(),
            x=int(self.request.GET.get("x", 0)),
            y=int(self.request.GET.get("y", 0)),
            z=int(self.request.GET.get("z", 17)),
        )
        return context

    def wialon_get_unit_position(self, session: WialonSession) -> dict:
        """
        Retrieves and returns the Wialon unit position for the view.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Unit position data.
        :rtype: :py:obj:`dict`

        """
        return self.wialon_get_unit(session).get_position()

    def wialon_get_unit(self, session: WialonSession) -> WialonUnit:
        """
        Retrieves and returns the Wialon unit for the view.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: The related Wialon unit for the view.
        :rtype: :py:obj:`~terminusgps.wialon.items.units.WialonUnit`

        """
        return WialonUnit(id=self.get_object().pk, session=session)

    def wialon_generate_map_url(
        self, session: WialonSession, x: int = 0, y: int = 0, z: int = 17
    ) -> str:
        """
        Generates and returns a URL to a map.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :param x: X-coordinate of tile. Default is :py:obj:`0`.
        :type x: :py:obj:`int`
        :param y: Y-coordinate of tile. Default is :py:obj:`0`.
        :type y: :py:obj:`int`
        :param z: Zoom level of tile. Default is :py:obj:`17`.
        :type z: :py:obj:`int`
        :returns: A url pointing to a map image file.
        :rtype: :py:obj:`str`

        """
        return f"http://hst-api.wialon.com/avl_render/{x}_{y}_{z}/{session.id}.png"


class WialonAssetCommandListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "command_list"
    extra_context = {"title": "Command", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = WialonAssetCommand
    partial_template_name = "terminusgps_installer/assets/partials/_command_list.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/assets/command_list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not kwargs.get("asset_pk"):
            return HttpResponse(status=406)
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        asset: WialonAsset | None = self._get_asset()
        return asset.commands.all() if asset is not None else WialonAsset.objects.none()

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["title"] = f"{self._get_asset().name} Commands"
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
        "class": "flex items-center justify-between gap-2 rounded border p-2",
    }
    context_object_name = "command"
    http_method_names = ["get", "patch"]
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
    extra_context = {
        "title": "Execute Command",
        "class": "flex items-center justify-between gap-2 rounded border p-2",
    }
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
    success_url = reverse_lazy("installer:command execute success")

    def get_success_url(self) -> str:
        return reverse(
            "installer:command execute success",
            kwargs={"asset_pk": self.kwargs["asset_pk"], "pk": self.kwargs["pk"]},
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["command"] = self._get_command()
        return context

    def _get_command(self) -> WialonAssetCommand | None:
        if self._get_asset() and self.kwargs.get("pk"):
            return self._get_asset().commands.get(pk=self.kwargs["pk"])

    def _get_asset(self) -> WialonAsset | None:
        if self.kwargs.get("asset_pk"):
            return WialonAsset.objects.get(pk=self.kwargs["asset_pk"])


class WialonAssetCommandExecuteSuccessView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    extra_context = {"title": "Command Executed"}
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
