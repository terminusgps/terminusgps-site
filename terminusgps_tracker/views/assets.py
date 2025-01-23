from typing import Any

from django import forms
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.db.models import QuerySet
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.list import ListView
from terminusgps.wialon import flags
from terminusgps.wialon.items import WialonUnit, WialonUser, WialonUnitGroup
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_iccid
from wialon.api import WialonError

from terminusgps_tracker.models import TrackerAsset, TrackerAssetCommand
from terminusgps_tracker.forms import TrackerAssetUpdateForm, TrackerAssetCreateForm
from terminusgps_tracker.views.base import TrackerBaseView
from terminusgps_tracker.views.mixins import (
    SubscriptionRequiredMixin,
    TrackerProfileSingleObjectMixin,
    TrackerProfileMultipleObjectMixin,
)


class WialonUnitNotFoundError(Exception):
    """Raised when a Wialon unit was not found via IMEI #."""


class AssetDeleteView(DeleteView, TrackerBaseView, TrackerProfileSingleObjectMixin):
    context_object_name = "asset"
    http_method_names = ["post"]
    model = TrackerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_delete.html"
    queryset = TrackerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/delete.html"
    success_url = reverse_lazy("tracker profile")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            session = WialonSession(sid=self.wialon_sid)
            unit = WialonUnit(id=self.get_object().wialon_id, session=session)
            user = WialonUser(id=self.profile.wialon_end_user_id, session=session)
            group = WialonUnitGroup(id=self.profile.wialon_group_id, session=session)
            fields = unit.cfields | unit.afields
            imei_number = str(
                {key.lower(): value for key, value in fields.items()}.get("iccid")
            )

            unit.rename(imei_number)
            group.rm_item(unit)
            user.grant_access(unit, access_mask=0)
        except WialonError:
            return self.render_to_response(context=self.get_context_data())
        return super().post(request, *args, **kwargs)


class AssetListView(ListView, TrackerBaseView, TrackerProfileMultipleObjectMixin):
    context_object_name = "asset_list"
    http_method_names = ["get", "post"]
    model = TrackerAsset
    paginate_by = 6
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    queryset = TrackerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/list.html"
    ordering = "name"


class AssetDetailView(DetailView, TrackerBaseView, TrackerProfileSingleObjectMixin):
    model = TrackerAsset
    queryset = TrackerAsset.objects.none()
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    template_name = "terminusgps_tracker/assets/detail.html"
    extra_context = {"title": "Asset Detail"}
    context_object_name = "asset"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        asset = self.get_object()
        asset.save(session=WialonSession(sid=self.wialon_sid))
        return self.render_to_response(self.get_context_data(**kwargs))


class AssetRemoteView(DetailView, TrackerBaseView, TrackerProfileSingleObjectMixin):
    model = TrackerAsset
    queryset = TrackerAsset.objects.none()
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/assets/partials/_remote.html"
    template_name = "terminusgps_tracker/assets/remote.html"
    extra_context = {"title": "Asset Remote"}
    context_object_name = "asset"


class AssetUpdateView(UpdateView, TrackerBaseView, TrackerProfileSingleObjectMixin):
    model = TrackerAsset
    queryset = TrackerAsset.objects.none()
    form_class = TrackerAssetUpdateForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/assets/partials/_update.html"
    template_name = "terminusgps_tracker/assets/update.html"
    extra_context = {"title": "Asset Update"}
    context_object_name = "asset"

    def get_success_url(self, asset: TrackerAsset | None = None) -> str:
        if asset:
            return asset.get_absolute_url()
        return reverse("tracker profile")

    def get_initial(self) -> dict[str, Any]:
        asset = self.get_object()

        initial: dict[str, Any] = super().get_initial()
        initial["imei_number"] = asset.imei_number
        initial["name"] = asset.name
        return initial

    def form_valid(self, form: forms.Form) -> HttpResponseRedirect | HttpResponse:
        asset = self.get_object()
        session = WialonSession(sid=self.wialon_sid)

        unit = WialonUnit(id=str(asset.wialon_id), session=session)
        unit.rename(form.cleaned_data["name"])
        return HttpResponseRedirect(self.get_success_url(asset))


class AssetCreateView(
    CreateView,
    TrackerBaseView,
    SubscriptionRequiredMixin,
    TrackerProfileSingleObjectMixin,
):
    context_object_name = "asset"
    extra_context = {
        "title": "New Asset",
        "subtitle": "Please enter a new name for your asset and an IMEI #",
    }
    form_class = TrackerAssetCreateForm
    http_method_names = ["get", "post", "delete"]
    login_url = reverse_lazy("tracker login")
    model = TrackerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    permission_denied_message = (
        "You must have an active subscription in order to add an asset."
    )
    queryset = TrackerAsset.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/assets/create.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.imei_number = request.GET.get("imei", "")
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = None
        return super().get_context_data(**kwargs)

    def get_initial(self) -> dict[str, Any]:
        if self.imei_number:
            return {"imei_number": self.imei_number}
        return super().get_initial()

    def get_success_url(self, asset: TrackerAsset | None = None) -> str:
        if asset is not None:
            return asset.get_absolute_url()
        return reverse("tracker profile")

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Only htmx can make DELETE requests
        return HttpResponse(status=200 if request.headers.get("HX-Request") else 403)

    def get_available_commands(self) -> QuerySet:
        return TrackerAssetCommand.objects.filter().exclude(pk__in=[1, 2, 3])

    def form_valid(self, form: forms.Form) -> HttpResponse:
        imei_number: str = form.cleaned_data["imei_number"]
        asset_name: str | None = form.cleaned_data["name"]

        try:
            session = WialonSession(sid=self.wialon_sid)
            unit_id: str | None = get_id_from_iccid(imei_number, session=session)
            if not unit_id:
                raise WialonUnitNotFoundError()

            self.wialon_create_asset(int(unit_id), asset_name or imei_number, session)
            asset = TrackerAsset.objects.create(
                wialon_id=unit_id,
                imei_number=imei_number,
                name=asset_name or imei_number,
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
                    _(
                        "Unit with IMEI # '%(value)s' may not exist, or wasn't found. Please verify IMEI #."
                    ),
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
        response = HttpResponseRedirect(self.get_success_url(asset))
        response.headers["HX-Request"] = True
        return response

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
