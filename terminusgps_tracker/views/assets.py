from typing import Any

from django.conf import settings
from django import forms
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
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
    partial_name = "terminusgps_tracker/assets/partials/_list.html"
    template_name = "terminusgps_tracker/assets/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = (
            TrackerProfile.objects.get(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )

    def get_queryset(self) -> QuerySet:
        if not self.profile:
            return TrackerAsset.objects.none()
        return self.profile.assets.all()


class AssetDetailView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/assets/detail.html"
    partial_name = "terminusgps_tracker/assets/partials/_detail.html"
    model = TrackerAsset
    context_object_name = "asset"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_queryset(self) -> QuerySet:
        return self.profile.assets.all()


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/assets/update.html"
    partial_name = "terminusgps_tracker/assets/partials/_update.html"
    fields = ["name", "imei_number"]
    context_object_name = "asset"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name


class AssetCreationView(LoginRequiredMixin, CreateView):
    content_type = "text/html"
    http_method_names = ["get", "post", "delete"]
    template_name = "terminusgps_tracker/assets/create.html"
    partial_name = "terminusgps_tracker/assets/partials/_create.html"
    fields = ["name", "imei_number"]
    context_object_name = "asset"
    model = TrackerAsset

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        self.profile = TrackerProfile.objects.get(user=request.user)

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return HttpResponse("")

    def get_available_commands(self) -> QuerySet:
        return TrackerAssetCommand.objects.filter().exclude(pk__in=[1, 2, 3])

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class)
        form.fields["name"].widget = forms.TextInput(
            {"class": "px-4 py-2 text-terminus-red-700 bg-red-100"}
        )
        form.fields["imei_number"].widget = forms.TextInput(
            {"class": "px-4 py-2 text-terminus-red-700 bg-red-100"}
        )
        return form

    @transaction.atomic
    def wialon_create_asset(self, id: str, name: str, session: WialonSession) -> None:
        assert self.profile.wialon_end_user_id
        end_user_id = self.profile.wialon_end_user_id

        available = WialonUnitGroup(
            id=str(settings.WIALON_UNACTIVATED_GROUP), session=session
        )
        user = WialonUser(id=str(end_user_id), session=session)
        unit = WialonUnit(id=id, session=session)

        available.rm_item(unit)
        unit.rename(name)
        user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_BASIC)

        asset = TrackerAsset.objects.create(id=unit.id, profile=self.profile)
        queryset = self.get_available_commands()
        asset.commands.set(queryset)
        asset.save()

    def form_valid(self, form: forms.Form) -> HttpResponse:
        imei_number: str = form.cleaned_data["imei_number"]

        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                unit_id: str | None = get_id_from_iccid(imei_number, session=session)
                if not unit_id:
                    raise WialonUnitNotFoundError()

                self.wialon_create_asset(
                    unit_id, form.cleaned_data["asset_name"], session
                )
        except AssertionError:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Couldn't find the Wialon user associated with this profile. Please try again later."
                    )
                ),
            )
            return self.form_invalid(form=form)
        except WialonUnitNotFoundError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _("Unit with IMEI # '%(imei)s' may not exist, or wasn't found."),
                    code="invalid",
                    params={"imei": imei_number},
                ),
            )
            return self.form_invalid(form=form)
        except WialonError or ValueError:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Something went wrong with Wialon. Please try again later."
                    )
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class AssetDeletionView(LoginRequiredMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["get", "delete"]
    template_name = "terminusgps_tracker/assets/delete.html"
    partial_name = "terminusgps_tracker/assets/partials/_delete.html"
    fields = ["id"]

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        return super().delete(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name


class CommandExecutionView(LoginRequiredMixin, FormView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    form_class = CommandExecutionForm
    template_name = "terminusgps_tracker/assets/remote_button.html"
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True

    def get_success_url(self) -> str:
        return reverse("execute command", kwargs={"id": self.asset.id})

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.asset = self.profile.assets.filter().get(pk=self.kwargs["id"])

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        return super().post(request, *args, **kwargs)

    def form_valid(
        self, form: CommandExecutionForm
    ) -> HttpResponse | HttpResponseRedirect:
        command: TrackerAssetCommand = form.cleaned_data["command"]
        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                command.execute(self.asset.id, session)
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.asset = self.profile.assets.filter().get(pk=self.kwargs["id"])
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            self.asset.save(session)

    def get_success_url(self) -> str:
        return reverse("asset remote", kwargs={"id": self.asset.id})

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["asset"] = self.asset
        context["title"] = f"{self.asset.name} Remote"
        context["commands"] = self.asset.commands.filter()
        return context
