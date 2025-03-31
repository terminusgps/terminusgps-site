from typing import Any

import wialon.api
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView
from terminusgps.wialon import constants
from terminusgps.wialon.items import (
    WialonResource,
    WialonUnit,
    WialonUnitGroup,
    WialonUser,
)
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_imei

from terminusgps_tracker.forms import CustomerAssetCreateForm
from terminusgps_tracker.models.customers import Customer, CustomerAsset
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    CustomerSubscriptionRequiredMixin,
    HtmxTemplateResponseMixin,
)


class CustomerAssetDetailView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {"class": "flex flex-col gap-4 border p-4 rounded bg-white"}
    http_method_names = ["get", "patch"]
    model = CustomerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    queryset = CustomerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/detail.html"

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer: Customer = Customer.objects.get(user=self.request.user)
        return customer.assets.filter()


class CustomerAssetCreateView(
    CustomerSubscriptionRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    context_object_name = "asset"
    extra_context = {"class": "flex flex-col gap-4 relative", "title": "Register Asset"}
    http_method_names = ["get", "post"]
    model = CustomerAsset
    form_class = CustomerAssetCreateForm
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    queryset = CustomerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/create.html"
    success_url = reverse_lazy("dashboard")

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["imei_number"] = self.request.GET.get("imei", "")
        initial["customer"] = (
            Customer.objects.get(user=self.request.user)
            if self.request.user and self.request.user.is_authenticated
            else None
        )
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerAssetCreateForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            with WialonSession() as session:
                customer: Customer = form.cleaned_data["customer"]
                imei_number: str = str(form.cleaned_data["imei_number"])
                unit_id: str | None = get_id_from_imei(imei_number, session)
                if unit_id is None:
                    form.add_error(
                        "imei_number",
                        ValidationError(
                            _("Whoops! Couldn't find a unit with IMEI '%(value)s'."),
                            code="invalid",
                            params={"value": imei_number},
                        ),
                    )
                    return self.form_invalid(form=form)
                if not customer.wialon_resource_id:
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! Customer does not have an assigned Wialon resource, please try again later."
                            ),
                            code="invalid",
                        ),
                    )
                    return self.form_invalid(form=form)
                if not customer.wialon_user_id:
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! Customer does not have an assigned Wialon user, please try again later."
                            )
                        ),
                    )
                    return self.form_invalid(form=form)

                user = WialonUser(id=customer.wialon_user_id, session=session)
                unit = WialonUnit(id=unit_id, session=session)
                resource = WialonResource(
                    id=customer.wialon_resource_id, session=session
                )

                resource.migrate_unit(unit)
                user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_BASIC)
                unit.rename(form.cleaned_data["name"])
                if customer.wialon_group_id:
                    group = WialonUnitGroup(
                        id=customer.wialon_group_id, session=session
                    )
                    group.add_item(unit)
                return super().form_valid(form=form)
        except (wialon.api.WialonError, AssertionError) as e:
            form.add_error(
                "imei_number",
                ValidationError(
                    _("Whoops! '%(error)s'"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)


class CustomerAssetListView(CustomerRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    context_object_name = "asset_list"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    model = CustomerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    queryset = CustomerAsset.objects.none()
    template_name = "terminusgps_tracker/assets/list.html"

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer: Customer = Customer.objects.get(user=self.request.user)
        return customer.assets.filter()


class CustomerAssetDeleteView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "asset"
    http_method_names = ["post"]
    model = CustomerAsset
    template_name = "terminusgps_tracker/assets/delete.html"
    partial_template_name = "terminusgps_tracker/assets/partials/_delete.html"
    queryset = CustomerAsset.objects.none()

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer: Customer = Customer.objects.get(user=self.request.user)
        return customer.assets.filter()
