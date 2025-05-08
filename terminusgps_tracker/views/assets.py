from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_unit_by_imei
from wialon.api import WialonError

from terminusgps_tracker.forms import CustomerAssetCreateForm
from terminusgps_tracker.models import Customer, CustomerAsset


class CustomerAssetListView(LoginRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    context_object_name = "asset_list"
    extra_context = {"title": "Asset List", "subtitle": "Your vehicles at a glance"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerAsset
    ordering = "wialon_id"
    paginate_by = 25
    partial_template_name = "terminusgps_tracker/assets/partials/_list.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/assets/list.html"

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer = Customer.objects.get(user=self.request.user)
        return super().get_queryset().filter(customer=customer)


class CustomerAssetDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "asset"
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerAsset
    partial_template_name = "terminusgps_tracker/assets/partials/_detail.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/assets/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        return context

    def get_queryset(self) -> QuerySet[CustomerAsset, CustomerAsset]:
        customer = Customer.objects.get(user=self.request.user)
        return super().get_queryset().filter(customer=customer)


class CustomerAssetCreateView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register Asset",
        "subtitle": "Add an asset to your account",
    }
    context_object_name = "asset"
    form_class = CustomerAssetCreateForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/assets/partials/_create.html"
    permission_required = "terminusgps_tracker.add_customerasset"
    template_name = "terminusgps_tracker/assets/create.html"

    def get_success_url(self, asset: CustomerAsset | None) -> str:
        if asset is not None:
            return asset.get_absolute_url()
        return reverse("tracker:list assets")

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["imei_number"] = self.request.GET.get("imei")
        return initial

    def form_valid(
        self, form: CustomerAssetCreateForm
    ) -> HttpResponse | HttpResponseRedirect:
        imei_number: str = form.cleaned_data["imei_number"]
        customer: Customer = Customer.objects.get(user=self.request.user)

        if not customer.wialon_user_id:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Your account doesn't have an assigned Wialon user. Please try again later."
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
                        "Whoops! Your account doesn't have an assigned Wialon resource. Please try again later."
                    ),
                    code="invalid",
                ),
            )

        try:
            with WialonSession() as session:
                unit_id = get_unit_by_imei(imei_number, session)
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

                if unit.name != form.cleaned_data["name"]:
                    unit.rename(form.cleaned_data["name"])
                resource.migrate_unit(unit)
                user.grant_access(unit, access_mask=constants.ACCESSMASK_UNIT_BASIC)

                asset = CustomerAsset.objects.create(
                    wialon_id=unit.id, customer=customer, name=form.cleaned_data["name"]
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
