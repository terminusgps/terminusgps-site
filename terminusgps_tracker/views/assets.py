from django.forms import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from wialon.api import WialonError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonUnit, WialonUnitGroup

from terminusgps_tracker.views.base import TrackerBaseView
from terminusgps_tracker.views.mixins import (
    TrackerProfileSingleObjectMixin,
    TrackerProfileMultipleObjectMixin,
)
from terminusgps_tracker.models import TrackerAsset
from terminusgps_tracker.forms import TrackerAssetCreateForm, TrackerAssetUpdateForm


class TrackerAssetDetailView(
    DetailView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    model = TrackerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    template_name = "terminusgps_tracker/assets/detail.html"


class TrackerAssetListView(
    ListView, TrackerBaseView, TrackerProfileMultipleObjectMixin
):
    allow_empty = True
    model = TrackerAsset
    ordering = "name"
    paginate_by = 3
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    template_name = "terminusgps_tracker/assets/list.html"


class TrackerAssetCreateView(
    CreateView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    extra_context = {
        "class": "flex flex-col p-4 gap-8 bg-gray-100 rounded border shadow"
    }
    form_class = TrackerAssetCreateForm
    model = TrackerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    success_url = reverse_lazy("asset list")
    template_name = "terminusgps_tracker/assets/create.html"

    def form_valid(self, form: TrackerAssetUpdateForm) -> HttpResponse:
        imei_number = form.cleaned_data["imei_number"]
        new_name = form.cleaned_data["name"] or form.cleaned_data["imei_number"]

        try:
            asset = TrackerAsset.objects.create(imei_number=imei_number)
            asset.save(session=self.wialon_session, populate=False)
            self.wialon_asset_registration_flow(asset, new_name=new_name)
            asset.save(session=self.wialon_session, populate=True)
            return super().form_valid(form=form)
        except WialonError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Something went wrong with Wialon: '%(error)s'"),
                    code="invalid",
                    params={"error": e},
                ),
            )
        except (AssertionError, ValueError) as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Something went wrong on our end: '%(error)s'"),
                    code="invalid",
                    params={"error": e},
                ),
            )
        return super().form_invalid(form=form)

    def wialon_asset_registration_flow(
        self, asset: TrackerAsset, new_name: str | None = None
    ) -> None:
        try:
            assert self.profile, "User profile was not set."
            assert asset.wialon_id, "Asset wialon id was not set."
            super_user = self.profile.get_super_user(self.wialon_session)
            end_user = self.profile.get_end_user(self.wialon_session)
            resource = self.profile.get_resource(self.wialon_session)
            unit_group = self.profile.get_group(self.wialon_session)
            unit = WialonUnit(id=asset.wialon_id, session=self.wialon_session)
        except AssertionError:
            raise

        super_user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION)
        end_user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_BASIC)
        resource.migrate_unit(unit)
        unit_group.add_item(unit)

        available = WialonUnitGroup(
            id=settings.WIALON_UNACTIVATED_GROUP, session=self.wialon_session
        )
        if unit.id in available.items:
            available.rm_item(unit)
        if new_name is not None:
            unit.rename(new_name)


class TrackerAssetUpdateView(
    UpdateView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    form_class = TrackerAssetUpdateForm
    model = TrackerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_update.html"
    success_url = reverse_lazy("asset list")
    template_name = "terminusgps_tracker/assets/update.html"

    def form_valid(self, form: TrackerAssetUpdateForm) -> HttpResponse:
        self.object = self.get_object()
        self.object.save(profile=self.profile, form=form, session=self.wialon_session)
        return super().form_valid(form=form)
