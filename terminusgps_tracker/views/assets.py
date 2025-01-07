from typing import Any

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.items import WialonUnit, WialonUser, WialonUnitGroup
from terminusgps.wialon import flags
from terminusgps.wialon.utils import get_id_from_iccid
from wialon.api import WialonError

from terminusgps_tracker.models.assets import TrackerAsset, TrackerAssetCommand
from terminusgps_tracker.models.profiles import TrackerProfile
from terminusgps_tracker.forms import (
    CommandExecutionForm,
    TrackerAssetUpdateForm,
    TrackerAssetCreateForm,
)


class WialonUnitNotFoundError(Exception):
    """Raised when a Wialon unit was not found via IMEI #."""


class AssetListView(LoginRequiredMixin, ListView):
    content_type = "text/html"
    context_object_name = "asset_list"
    http_method_names = ["get"]
    model = TrackerAsset
    paginate_by = 6
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    template_name = "terminusgps_tracker/assets/list.html"
    login_url = reverse_lazy("tracker login")
    raise_exception = False
    permission_denied_message = "Please login and try again."

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

    def get_queryset(self) -> QuerySet:
        if not self.profile:
            return TrackerAsset.objects.none()
        return self.profile.assets.filter().order_by("name")


class AssetDetailView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/assets/detail.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    model = TrackerAsset
    context_object_name = "asset"
    login_url = reverse_lazy("tracker login")
    raise_exception = False
    permission_denied_message = "Please login and try again."

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

    def get_queryset(self) -> QuerySet:
        return self.profile.assets.all()


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/assets/update.html"
    partial_name = "terminusgps_tracker/assets/partials/_update.html"
    context_object_name = "asset"
    model = TrackerAsset
    form_class = TrackerAssetUpdateForm
    success_url = reverse_lazy("tracker profile")
    login_url = reverse_lazy("tracker login")
    raise_exception = False
    permission_denied_message = "Please login and try again."

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["imei_number"] = self.get_object().imei_number
        return initial

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name

    def get_queryset(self) -> QuerySet:
        if self.profile:
            return self.profile.assets.filter()
        return TrackerAsset.objects.none()

    @transaction.atomic
    def form_valid(self, form: forms.Form) -> HttpResponseRedirect | HttpResponse:
        with WialonSession() as session:
            unit = WialonUnit(id=str(self.kwargs["pk"]), session=session)
            unit.rename(form.cleaned_data["name"])
        return super().form_valid(form=form)


class AssetCreateView(LoginRequiredMixin, CreateView):
    content_type = "text/html"
    http_method_names = ["get", "post", "delete"]
    template_name = "terminusgps_tracker/assets/create.html"
    partial_name = "terminusgps_tracker/assets/partials/_create.html"
    success_url = reverse_lazy("tracker profile")
    context_object_name = "asset"
    model = TrackerAsset
    form_class = TrackerAssetCreateForm
    login_url = reverse_lazy("tracker login")
    raise_exception = False
    permission_denied_message = "Please login and try again."

    def get_success_url(self, asset: TrackerAsset | None = None) -> str:
        if asset is not None:
            return reverse("asset detail", kwargs={"pk": asset.pk})
        return str(self.success_url)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        return HttpResponse("", status=200)

    def form_valid(self, form: forms.Form) -> HttpResponse:
        imei_number: str = form.cleaned_data["imei_number"]
        asset_name: str | None = form.cleaned_data["name"]

        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                unit_id: str | None = get_id_from_iccid(imei_number, session=session)
                if not unit_id:
                    raise WialonUnitNotFoundError()

                self.wialon_create_asset(int(unit_id), asset_name, session)
                asset = TrackerAsset.objects.create(
                    wialon_id=unit_id,
                    imei_number=imei_number,
                    name=asset_name if asset_name else imei_number,
                )
                asset.profile = self.profile
                asset.commands.set(self.get_available_commands())
                asset.save()
        except AssertionError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "Unit with IMEI # '%(value)s' appears to have already been registered. Please try again later."
                    ),
                    code="invalid",
                    params={"value": imei_number},
                ),
            )
            return self.form_invalid(form=form)
        except WialonUnitNotFoundError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _("Unit with IMEI # '%(value)s' may not exist, or wasn't found."),
                    code="invalid",
                    params={"value": imei_number},
                ),
            )
            return self.form_invalid(form=form)
        except WialonError or ValueError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "Whoops! Something went wrong with Wialon. Please try again later."
                    ),
                    code="wialon",
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)

    def get_available_commands(self) -> QuerySet:
        return TrackerAssetCommand.objects.filter().exclude(pk__in=[1, 2, 3])

    @transaction.atomic
    def wialon_create_asset(
        self, unit_id: int, name: str | None, session: WialonSession
    ) -> None:
        assert self.profile.wialon_end_user_id, "No end user id was set."
        assert self.profile.wialon_group_id, "No profile group was set."
        available = WialonUnitGroup(
            id=str(settings.WIALON_UNACTIVATED_GROUP), session=session
        )
        user = WialonUser(id=str(self.profile.wialon_end_user_id), session=session)
        unit = WialonUnit(id=str(unit_id), session=session)
        unit_group = WialonUnitGroup(
            id=str(self.profile.wialon_group_id), session=session
        )

        available.rm_item(unit)
        unit_group.add_item(unit)
        if name is not None:
            unit.rename(name)

        try:
            for item in unit, unit_group:
                session.wialon_api.user_update_item_access(
                    **{
                        "userId": str(user.id),
                        "itemId": str(item.id),
                        "accessMask": sum(
                            [
                                flags.ACCESSFLAG_VIEW_ITEM_BASIC,
                                flags.ACCESSFLAG_VIEW_ITEM_DETAILED,
                                flags.ACCESSFLAG_RENAME_ITEM,
                                flags.ACCESSFLAG_VIEW_CUSTOM_FIELDS,
                                flags.ACCESSFLAG_MANAGE_CUSTOM_FIELDS,
                                flags.ACCESSFLAG_MANAGE_ICON,
                                flags.ACCESSFLAG_VIEW_ADMIN_FIELDS,
                                flags.ACCESSFLAG_UNIT_IMPORT_MESSAGES,
                                flags.ACCESSFLAG_UNIT_EXPORT_MESSAGES,
                                flags.ACCESSFLAG_UNIT_VIEW_SERVICE_INTERVALS,
                            ]
                        ),
                    }
                )
        except WialonError as e:
            print(e)
            raise


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/assets/delete.html"
    partial_name = "terminusgps_tracker/assets/partials/_delete.html"
    model = TrackerAsset
    success_url = reverse_lazy("tracker profile")
    login_url = reverse_lazy("tracker login")
    raise_exception = False
    permission_denied_message = "Please login and try again."

    @staticmethod
    def wialon_delete_asset(unit_id: int, session: WialonSession) -> None:
        available_group_id: int = settings.WIALON_UNACTIVATED_GROUP

    def get_queryset(self) -> QuerySet:
        if self.profile is not None:
            return self.profile.assets.filter()
        return TrackerAsset.objects.none()

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.htmx_request:
            return HttpResponse(status=402)
        return super().delete(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.unit_id = self.kwargs.get("pk")
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )
        self.group_id = (
            self.profile.wialon_resource_id if self.profile is not None else None
        )
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_name


class CommandExecutionView(LoginRequiredMixin, FormView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    form_class = CommandExecutionForm
    template_name = "terminusgps_tracker/assets/remote_button.html"
    partial_template_name = "terminusgps_tracker/assets/_remote_button.html"
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def get_success_url(self) -> str:
        return reverse("execute command", kwargs={"id": self.asset.id})

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.asset = self.profile.assets.filter().get(pk=self.kwargs["id"])
        self.htmx_request = bool(request.headers.get("HX-Request"))
        self.wialon_session = WialonSession(token=settings.WIALON_TOKEN)
        self.wialon_session.login()
        if self.htmx_request:
            self.template_name = self.partial_template_name

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.htmx_request:
            return HttpResponse(status=403)
        return super().post(request, *args, **kwargs)

    def form_valid(
        self, form: CommandExecutionForm
    ) -> HttpResponse | HttpResponseRedirect:
        command: TrackerAssetCommand = form.cleaned_data["command"]
        try:
            command.execute(self.asset.id, self.wialon_session)
        except WialonError or ValueError:
            form.add_error(
                "command",
                ValidationError(
                    _("Whoops! We couldn't execute '%(cmd)s'. Please try again later."),
                    code="invalid",
                    params={"cmd": command.name},
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class AssetRemoteView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    template_name = "terminusgps_tracker/assets/remote.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_remote.html"
    model = TrackerAsset

    def get_queryset(self) -> QuerySet:
        if self.profile is not None:
            return self.profile.assets.all()
        return TrackerAsset.objects.none()

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        asset: TrackerAsset = self.get_object()
        context["asset"] = asset
        context["title"] = f"{asset.name} Remote"
        context["commands"] = asset.commands.all()
        return context
