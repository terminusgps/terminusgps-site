from typing import Any

from django import forms
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.forms import ValidationError
from django.http.response import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView, MultipleObjectMixin
from terminusgps.wialon import flags
from terminusgps.wialon.items import WialonUnit, WialonUser, WialonUnitGroup
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_iccid
from wialon.api import WialonError

from terminusgps_tracker.models import TrackerAsset, TrackerAssetCommand
from terminusgps_tracker.forms import TrackerAssetUpdateForm, TrackerAssetCreateForm
from terminusgps_tracker.views.mixins import HtmxMixin, ProfileContextMixin


class WialonUnitNotFoundError(Exception):
    """Raised when a Wialon unit was not found via IMEI #."""


class AssetDeleteView(DeleteView, ProfileContextMixin, HtmxMixin):
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/assets/partials/_delete.html"
    template_name = "terminusgps_tracker/assets/delete.html"
    extra_context = {"title": "Delete Asset"}


class AssetListView(ListView, ProfileContextMixin, HtmxMixin):
    context_object_name = "asset_list"
    paginate_by = 6
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    template_name = "terminusgps_tracker/assets/list.html"
    extra_context = {"title": "List Assets"}


class AssetDetailView(DetailView, ProfileContextMixin, HtmxMixin):
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    template_name = "terminusgps_tracker/assets/detail.html"
    extra_context = {"title": "Asset Detail"}


class AssetRemoteView(DetailView, ProfileContextMixin, HtmxMixin):
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/assets/partials/_remote.html"
    template_name = "terminusgps_tracker/assets/remote.html"
    extra_context = {"title": "Asset Remote"}


class AssetUpdateView(UpdateView, ProfileContextMixin, HtmxMixin):
    form_class = TrackerAssetUpdateForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/assets/partials/_update.html"
    template_name = "terminusgps_tracker/assets/update.html"
    extra_context = {"title": "Asset Update"}

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["imei_number"] = self.get_object().imei_number
        return initial

    def form_valid(self, form: forms.Form) -> HttpResponseRedirect | HttpResponse:
        with WialonSession() as session:
            unit = WialonUnit(id=str(self.kwargs["pk"]), session=session)
            unit.rename(form.cleaned_data["name"])
        return HttpResponseRedirect(self.get_success_url(self.get_object()))


class AssetCreateView(CreateView, ProfileContextMixin, HtmxMixin):
    form_class = TrackerAssetCreateForm
    http_method_names = ["get", "post", "delete"]
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    template_name = "terminusgps_tracker/assets/create.html"

    def get_available_commands(self) -> QuerySet:
        return TrackerAssetCommand.objects.filter().exclude(pk__in=[1, 2, 3])

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
