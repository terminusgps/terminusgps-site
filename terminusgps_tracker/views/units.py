import typing

from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants as wialon_constants
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
        if unit is not None and request.GET.get("refresh") == "on":
            with WialonSession() as session:
                unit.wialon_sync(session)
                unit.save()
        return super().get(request, *args, **kwargs)


class CustomerWialonUnitListDeleteView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DeleteView,
):
    content_type = "text/html"
    context_object_name = "unit"
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = (
        "terminusgps_tracker/units/partials/_list_delete.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "unit_pk"
    queryset = CustomerWialonUnit.objects.select_related("customer", "tier")
    raise_exception = False
    template_name = "terminusgps_tracker/units/list_delete.html"

    def get_success_url(self) -> str:
        return reverse(
            "tracker:unit list",
            kwargs={"customer_pk": self.kwargs["customer_pk"]},
        )

    def form_valid(self, form: forms.Form) -> HttpResponse:
        if (
            Customer.objects.get(pk=self.kwargs["customer_pk"]).units.count()
            == 1
        ):
            form.add_error(
                None,
                ValidationError(_("Whoops! You can't delete your last unit.")),
            )
            response = self.form_invalid(form=form)
            response.headers["HX-Retarget"] = f"#unit-{self.kwargs['unit_pk']}"
            return response

        response = super().form_valid(form=form)
        subscription = Subscription.objects.get(
            customer=Customer.objects.get(pk=self.kwargs["customer_pk"])
        )
        subscription.authorizenet_update_amount(
            subscription.authorizenet_get_subscription_profile()
        )
        return response


class CustomerWialonUnitListUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
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

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class=form_class)
        for name in form.fields:
            form.fields[name].widget.attrs.update(
                {"class": settings.DEFAULT_FIELD_CLASS}
            )
        return form

    def get_success_url(self) -> str:
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
        try:
            sub = Subscription.objects.get(
                customer__pk=self.kwargs["customer_pk"]
            )
        except Subscription.DoesNotExist:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! You need to be subscribed to do that.")
                ),
            )
            return self.form_invalid(form=form)

        response = super().form_valid(form=form)
        sprofile = sub.authorizenet_get_subscription_profile()
        sub.authorizenet_update_amount(sprofile)
        with WialonSession() as session:
            new_name = form.cleaned_data["name"]
            unit = WialonUnit(self.get_object().pk, session)

            if new_name != unit.name:
                unit.rename(new_name)
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

    def wialon_unit_exists(self, imei_number: str) -> bool:
        """Checks if a Wialon unit exists by imei number."""
        with WialonSession() as session:
            return bool(
                wialon_utils.get_unit_by_imei(
                    imei=imei_number, session=session
                )
            )

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["name"] = f"{self.request.user.first_name}'s Ride"
        initial["imei"] = self.request.GET.get("imei")
        return initial

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Validates the form data before doing anything with the Wialon API."""
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form=form)

        customer = Customer.objects.get(user=request.user)
        username = (
            customer.user.email
            if customer.user.email
            else customer.user.username
        )

        if not customer.wialon_resource_id:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! There's no Wialon account associated with '%(email)s'. Please try again later."
                    ),
                    code="invalid",
                    params={"email": username},
                ),
            )
        if not customer.wialon_user_id:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! There's no Wialon user associated with '%(email)s'. Please try again later."
                    ),
                    code="invalid",
                    params={"email": username},
                ),
            )
        if not customer.payments.exists():
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Please add at least one payment method first."),
                    code="invalid",
                ),
            )
        if not customer.addresses.exists():
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Please add at least one shipping address first."
                    ),
                    code="invalid",
                ),
            )

        return (
            self.form_valid(form=form)
            if form.is_valid()
            else self.form_invalid(form=form)
        )

    def form_valid(
        self, form: CustomerWialonUnitCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        """
        Retrieves a unit from Wialon and creates a :model:`terminusgps_tracker.CustomerWialonUnit` based on it.

        Also grants necessary permissions to the customer to view the unit in Wialon.

        """
        with WialonSession() as session:
            customer = Customer.objects.get(user=self.request.user)
            unit: WialonUnit = wialon_utils.get_unit_by_imei(
                imei=form.cleaned_data["imei"], session=session
            )
            resource = WialonResource(
                id=customer.wialon_resource_id, session=session
            )
            end_user = WialonUser(id=customer.wialon_user_id, session=session)

            end_user.grant_access(
                unit, access_mask=wialon_constants.ACCESSMASK_UNIT_BASIC
            )
            unit.rename(form.cleaned_data["name"])
            resource.migrate_unit(unit)
            CustomerWialonUnit.objects.create(
                id=unit.id,
                name=unit.name,
                imei=unit.imei_number,
                customer=customer,
                tier=form.cleaned_data["tier"],
            )
        return HttpResponseRedirect(self.get_success_url())
