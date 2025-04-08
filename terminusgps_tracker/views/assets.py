from typing import Any

from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_imei
from wialon.api import WialonError

from terminusgps_tracker.forms import CustomerAssetCreateForm
from terminusgps_tracker.models import Customer, CustomerAsset
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
)


class CustomerAssetListView(CustomerRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    extra_context = {"title": "Asset List", "subtitle": "Your vehicles at a glance"}
    context_object_name = "asset_list"
    model = CustomerAsset
    paginate_by = 25
    ordering = "wialon_id"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/assets/list.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer = Customer.objects.get(user=self.request.user)
        return super().get_queryset().filter(customer=customer)


class CustomerAssetDetailView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "asset"
    model = CustomerAsset
    http_method_names = ["get", "patch"]
    template_name = "terminusgps_tracker/assets/detail.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        return context

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer = Customer.objects.get(user=self.request.user)
        return super().get_queryset().filter(customer=customer)


class CustomerAssetCreateView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {
        "title": "Register Asset",
        "subtitle": "Add an asset to your account",
    }
    context_object_name = "asset"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/assets/create.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    form_class = CustomerAssetCreateForm

    def get_success_url(self, asset: CustomerAsset | None) -> str:
        if asset is not None:
            return asset.get_absolute_url()
        return reverse("list assets")

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["imei_number"] = self.request.GET.get("imei")
        return initial

    def form_valid(
        self, form: CustomerAssetCreateForm
    ) -> HttpResponse | HttpResponseRedirect:
        imei_number: str = form.cleaned_data["imei_number"]
        asset_name: str = form.cleaned_data["name"]
        customer: Customer = Customer.objects.get(user=self.request.user)

        if not customer.wialon_user_id:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Your account doesn't have a Wialon user assigned to it. Please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        if not customer.wialon_resource_id:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Your account doesn't have a Wialon account assigned to it. Please try again later."
                    ),
                    code="invalid",
                ),
            )

        try:
            with WialonSession() as session:
                unit_id = get_id_from_imei(imei_number, session)  # Try to get unit id
                if unit_id is None:
                    form.add_error(
                        "imei_number",
                        ValidationError(
                            _(
                                "Whoops! No unit with that IMEI # is available. Please try again later."
                            ),
                            code="invalid",
                        ),
                    )
                    return self.form_invalid(form=form)

                unit = WialonUnit(id=unit_id, session=session)
                user = WialonUser(id=customer.wialon_user_id, session=session)
                resource = WialonResource(
                    id=customer.wialon_resource_id, session=session
                )
                if unit.name != asset_name:
                    unit.rename(asset_name)
                resource.migrate_unit(unit)
                user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_BASIC)

                asset = CustomerAsset.objects.create(
                    wialon_id=unit.id, customer=customer, name=asset_name
                )
                return HttpResponseRedirect(self.get_success_url(asset))
        except WialonError as e:
            form.add_error(
                "imei_number",
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
