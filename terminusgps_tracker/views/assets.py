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
    TemplateView,
    UpdateView,
)
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.items import WialonUnit, WialonUser, WialonUnitGroup
from terminusgps.wialon import constants
from terminusgps.wialon.utils import get_id_from_iccid
from wialon.api import WialonError

from terminusgps_tracker.models.assets import TrackerAsset, TrackerAssetCommand
from terminusgps_tracker.models.profiles import TrackerProfile
from terminusgps_tracker.forms import CommandExecutionForm


class WialonUnitNotFoundError(Exception):
    """Raised when a Wialon unit was not found via IMEI #."""


class AssetListView(LoginRequiredMixin, ListView):
    content_type = "text/html"
    context_object_name = "asset_list"
    http_method_names = ["get"]
    model = TrackerAsset
    ordering = "-name"
    paginate_by = 6
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    template_name = "terminusgps_tracker/assets/list.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_template_name

    def get_queryset(self) -> QuerySet:
        if not self.profile:
            return TrackerAsset.objects.none()
        return self.profile.assets.all()


class AssetDetailView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/assets/detail.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    model = TrackerAsset
    context_object_name = "asset"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_template_name

    def get_queryset(self) -> QuerySet:
        return self.profile.assets.all()


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/assets/update.html"
    partial_name = "terminusgps_tracker/assets/partials/_update.html"
    fields = ["name", "imei_number"]
    context_object_name = "asset"
    model = TrackerAsset

    def get_success_url(self, asset: TrackerAsset | None = None) -> str:
        if asset is None:
            return reverse("tracker profile")
        return reverse("asset detail", kwargs={"pk": asset.pk})

    def get_queryset(self) -> QuerySet:
        if self.profile:
            return self.profile.assets.filter()
        return TrackerAsset.objects.none()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for name in form.fields.keys():
            form.fields[name].widget.attrs.update(
                {"class": "p-2 rounded bg-gray-200 text-gray-700"}
            )
            if name == "name":
                form.fields[name].widget.attrs.update({"placeholder": "Asset Name"})
        return form

    @transaction.atomic
    def form_valid(self, form: forms.Form) -> HttpResponseRedirect | HttpResponse:
        if "name" in form.changed_data:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                unit = WialonUnit(id=str(self.kwargs["pk"]), session=session)
                unit.rename(form.cleaned_data["name"])
        return super().form_valid(form=form)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_name


class AssetCreationView(LoginRequiredMixin, CreateView):
    content_type = "text/html"
    http_method_names = ["get", "post", "delete"]
    template_name = "terminusgps_tracker/assets/create.html"
    partial_name = "terminusgps_tracker/assets/partials/_create.html"
    fields = ["name", "imei_number"]
    context_object_name = "asset"
    model = TrackerAsset

    def get_success_url(self, asset: TrackerAsset | None = None) -> str:
        if asset is None:
            return reverse("tracker profile")
        return reverse("detail asset", kwargs={"pk": asset.pk})

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.wialon_end_user_id = self.profile.wialon_end_user_id
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_name

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.htmx_request:
            return HttpResponse(status=402)
        return HttpResponse("", status=200)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for name in form.fields.keys():
            form.fields[name].widget.attrs.update({"class": "p-2 rounded bg-gray-200"})
            if name == "imei_number":
                form.fields[name].widget.attrs.update({"placeholder": "IMEI #"})
            if name == "name":
                form.fields[name].widget.attrs.update({"placeholder": "Asset Name"})
        return form

    def form_invalid(self, form: forms.Form) -> HttpResponse:
        for field in form.fields:
            if field in form.errors.keys():
                form.fields[field].widget.attrs.update(
                    {
                        "class": "p-2 rounded bg-red-50 text-terminus-red-700 placeholder-terminus-red-300"
                    }
                )
            else:
                form.fields[field].widget.attrs.update(
                    {
                        "class": "p-2 rounded bg-green-50 text-green-700 placeholder-green-300"
                    }
                )
        return super().form_invalid(form=form)

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
        assert self.wialon_end_user_id, "No end user id was set."
        available = WialonUnitGroup(
            id=str(settings.WIALON_UNACTIVATED_GROUP), session=session
        )
        user = WialonUser(id=str(self.wialon_end_user_id), session=session)
        unit = WialonUnit(id=str(unit_id), session=session)

        available.rm_item(unit)
        user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_BASIC)
        if name is not None:
            unit.rename(name)


class AssetDeletionView(LoginRequiredMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["get", "delete"]
    template_name = "terminusgps_tracker/assets/delete.html"
    partial_name = "terminusgps_tracker/assets/partials/_delete.html"
    fields = ["id"]

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.htmx_request:
            return HttpResponse(status=402)
        return super().delete(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
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
    raise_exception = True

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


class AssetRemoteView(LoginRequiredMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    template_name = "terminusgps_tracker/assets/remote.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_remote.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.htmx_request = bool(request.headers.get("HX-Request"))
        if self.htmx_request:
            self.template_name = self.partial_template_name
        try:
            self.asset = self.profile.assets.filter().get(pk=self.kwargs["id"])
        except TrackerAsset.DoesNotExist:
            self.asset = None

    def get_success_url(self) -> str:
        assert self.asset and self.asset.id, "Asset was not set"
        return reverse("asset remote", kwargs={"id": self.asset.id})

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.asset:
            context["asset"] = self.asset
            context["title"] = f"{self.asset.name} Remote"
            context["commands"] = self.asset.commands.all()
        return context
