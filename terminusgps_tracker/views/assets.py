from typing import Any

from django import forms
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.db import transaction
from django.views.generic import CreateView, DetailView, UpdateView
from django.views.generic.list import ListView

from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.items import WialonUnit, WialonUnitGroup, WialonUser
from terminusgps.wialon.utils import get_id_from_iccid
from terminusgps_tracker.forms.assets import (
    TrackerAssetCreateForm,
    TrackerAssetUpdateForm,
)
from terminusgps_tracker.models import TrackerAsset
from terminusgps_tracker.views.base import TrackerBaseView
from terminusgps_tracker.views.mixins import (
    SubscriptionRequiredMixin,
    TrackerProfileSingleObjectMixin,
    TrackerProfileMultipleObjectMixin,
)


class AssetTableView(ListView, TrackerBaseView, TrackerProfileMultipleObjectMixin):
    allow_empty = True
    context_object_name = "asset_list"
    content_type = "text/html"
    extra_context = {
        "title": "Your Assets",
        "subtitle": "Add or modify your registered assets below",
    }
    http_method_names = ["get"]
    model = TrackerAsset
    ordering = "name"
    paginate_by = 6
    queryset = TrackerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/table.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_table.html"


class AssetCreateView(CreateView, TrackerBaseView, TrackerProfileSingleObjectMixin):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {
        "title": "New Asset",
        "subtitle": "Fill in a name and the IMEI # for your new asset",
    }
    form_class = TrackerAssetCreateForm
    http_method_names = ["get", "post", "delete"]
    model = TrackerAsset
    queryset = TrackerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/create.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    success_url = reverse_lazy("tracker profile")

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return HttpResponse(status=200 if request.headers.get("HX-Request") else 403)

    @transaction.atomic
    def form_valid(self, form: TrackerAssetCreateForm) -> HttpResponseRedirect:
        session = WialonSession(sid=self.wialon_sid)
        asset = TrackerAsset.objects.create(
            profile=self.profile, imei_number=form.cleaned_data["imei_number"]
        )
        asset.save(session)
        return HttpResponseRedirect(self.get_success_url(asset))

    def get_success_url(self, asset: TrackerAsset | None = None) -> str:
        if asset is not None:
            return asset.get_absolute_url()
        return self.success_url

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = None
        return super().get_context_data(**kwargs)

    def get_initial(self, **kwargs) -> dict[str, Any]:
        initial = super().get_initial(**kwargs)
        initial["imei_number"] = self.request.GET.get("imei")
        return initial


class AssetDetailView(DetailView, TrackerBaseView, TrackerProfileSingleObjectMixin):
    content_type = "text/html"
    context_object_name = "asset"
    http_method_names = ["get"]
    model = TrackerAsset
    queryset = TrackerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/detail.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name.title()
        return context


class AssetUpdateView(UpdateView, TrackerBaseView, TrackerProfileSingleObjectMixin):
    content_type = "text/html"
    context_object_name = "asset"
    http_method_names = ["get", "post", "delete"]
    form_class = TrackerAssetUpdateForm
    model = TrackerAsset
    queryset = TrackerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/update.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_update.html"
    success_url = reverse_lazy("tracker profile")

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        asset = self.get_object()
        if asset is not None:
            initial["name"] = asset.name
            initial["imei_number"] = asset.imei_number
        return initial

    @transaction.atomic
    def form_valid(self, form: TrackerAssetUpdateForm) -> HttpResponseRedirect:
        asset = self.get_object()

        if asset is not None:
            session = WialonSession(sid=self.wialon_sid)
            unit = WialonUnit(id=asset.wialon_id, session=session)
            unit.rename(form.cleaned_data["name"])
            asset.save(session)
        return HttpResponseRedirect(self.get_success_url(self.get_object()))

    def get_success_url(self, asset: TrackerAsset | None = None) -> str:
        if asset is not None:
            return asset.get_absolute_url()
        return super().get_success_url()
