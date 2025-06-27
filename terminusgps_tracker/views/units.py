import typing

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, UpdateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.forms import CustomerWialonUnitCreationForm
from terminusgps_tracker.models import (
    Customer,
    CustomerWialonUnit,
    Subscription,
)
from terminusgps_tracker.views.mixins import CustomerOrStaffRequiredMixin


class CustomerWialonUnitDetailView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Unit Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_detail.html"
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/detail.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return (
            super()
            .get_queryset()
            .filter(customer__pk=self.kwargs["customer_pk"])
        )


class CustomerWialonUnitListView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    ListView,
):
    content_type = "text/html"
    context_object_name = "unit_list"
    extra_context = {"title": "Unit List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    ordering = "name"
    partial_template_name = "terminusgps_tracker/units/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return (
            super()
            .get_queryset()
            .filter(customer__pk=self.kwargs["customer_pk"])
            .order_by(self.get_ordering())
        )


class CustomerWialonUnitListDetailView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Unit Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = (
        "terminusgps_tracker/units/partials/_list_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list_detail.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        unit = self.get_object()

        if (
            unit is not None
            and request.GET.get("refresh") == "on"
            or unit.wialon_needs_sync()
        ):
            with WialonSession() as session:
                unit.wialon_sync(session)
                unit.save()
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        return (
            super()
            .get_queryset()
            .filter(customer__pk=self.kwargs["customer_pk"])
        )


class CustomerWialonUnitListUpdateView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    UpdateView,
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Update Unit"}
    fields = ["name", "tier"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = (
        "terminusgps_tracker/units/partials/_list_update.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list_update.html"

    def get_queryset(self) -> QuerySet[CustomerWialonUnit, CustomerWialonUnit]:
        """Returns a queryset of units for the customer."""
        return (
            super()
            .get_queryset()
            .filter(customer__pk=self.kwargs["customer_pk"])
        )

    def get_form(self, form_class=None) -> forms.Form:
        """Returns a styled update form."""
        form = super().get_form(form_class=form_class)
        for name in form.fields:
            form.fields[name].widget.attrs.update(
                {"class": settings.DEFAULT_FIELD_CLASS}
            )
        return form

    def get_success_url(self) -> str:
        """Returns a URL pointing to the unit's list detail view."""
        return reverse(
            "tracker:unit list detail",
            kwargs={
                "customer_pk": self.kwargs["customer_pk"],
                "unit_pk": self.get_object().pk,
            },
        )

    def form_valid(
        self, form: forms.Form
    ) -> HttpResponse | HttpResponseRedirect:
        customer_unit = self.get_object()
        old_tier = customer_unit.tier
        response = super().form_valid(form=form)

        with WialonSession() as session:
            unit = WialonUnit(customer_unit.pk, session)
            unit.rename(form.cleaned_data["name"])
        if form.cleaned_data["tier"] != old_tier:
            sub = Subscription.objects.get(customer=customer_unit.customer)
            sprofile = sub.authorizenet_get_subscription_profile()
            sub.authorizenet_update_amount(sprofile)
        return response


class CustomerWialonUnitCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Unit"}
    form_class = CustomerWialonUnitCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/units/partials/_create.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    success_url = reverse_lazy("tracker:units")
    template_name = "terminusgps_tracker/units/create.html"

    def wialon_get_unit(
        self, imei_number: str, session: WialonSession
    ) -> WialonUnit:
        unit = wialon_utils.get_unit_by_imei(imei=imei_number, session=session)
        if unit is None:
            raise ValueError("Couldn't find a unit with that imei number.")
        return unit

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["name"] = f"{self.request.user.first_name}'s Ride"
        initial["imei"] = self.request.GET.get("imei")
        return initial

    def form_valid(
        self, form: CustomerWialonUnitCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Retrieves a unit from Wialon and creates a :model:`terminusgps_tracker.CustomerWialonUnit` based on it.

        Also grants necessary permissions to the customer to view the unit in Wialon.

        """
        try:
            with WialonSession() as session:
                unit = self.wialon_get_unit(form.cleaned_data["imei"], session)

                customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
                resource = WialonResource(customer.wialon_resource_id, session)
                end_user = WialonUser(customer.wialon_user_id, session)
                super_user = WialonUser(resource.creator_id, session)
                unit.rename(form.cleaned_data["name"])

                super_user.grant_access(
                    unit, access_mask=constants.ACCESSMASK_UNIT_MIGRATION
                )
                end_user.grant_access(unit)
                resource.migrate_unit(unit)

                CustomerWialonUnit.objects.create(
                    customer=customer,
                    id=unit.id,
                    name=form.cleaned_data["name"],
                    imei=form.cleaned_data["imei"],
                    tier=form.cleaned_data["tier"],
                )
            return super().form_valid(form=form)
        except ValueError:
            form.add_error(
                "imei",
                ValidationError(
                    _("Couldn't find a device with this IMEI #."),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
