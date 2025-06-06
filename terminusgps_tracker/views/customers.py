import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView, TemplateView
from terminusgps.authorizenet.constants import ANET_XML_NS
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.authorizenet.profiles import AddressProfile, PaymentProfile
from terminusgps.authorizenet.utils import (
    generate_customer_address,
    generate_customer_payment,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants as wialon_constants
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.forms import (
    CustomerPaymentMethodCreationForm,
    CustomerShippingAddressCreationForm,
    CustomerWialonUnitCreationForm,
)
from terminusgps_tracker.models.customers import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    CustomerWialonUnit,
)


class CustomerDashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": settings.TRACKER_APP_CONFIG["MOTD"],
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_dashboard.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/dashboard.html"


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Account",
        "subtitle": "Update your payment information",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_account.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/account.html"


class CustomerSubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Your Subscription",
        "subtitle": "Update your subscription plan",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_subscription.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscription.html"


class CustomerTransactionsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Transactions",
        "subtitle": "Inspect your subscription transactions",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_transactions.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/transactions.html"


class CustomerSupportView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Support",
        "subtitle": "Drop us a line and we'll get in touch",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_support.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/support.html"


class CustomerWialonUnitsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Units",
        "subtitle": "Your currently active units",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_units.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/units.html"


class CustomerWialonUnitDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "unit"
    extra_context = {"title": "Unit Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_detail.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerWialonUnit.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/units/detail.html"

    def get_queryset(self):
        return CustomerWialonUnit.objects.filter(
            customer__user=self.request.user
        )


class CustomerWialonUnitListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    context_object_name = "unit_list"
    extra_context = {"title": "Unit List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerWialonUnit
    partial_template_name = "terminusgps_tracker/units/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerWialonUnit.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/units/list.html"

    def get_queryset(self):
        return CustomerWialonUnit.objects.filter(
            customer__user=self.request.user
        )


class CustomerWialonUnitCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Unit"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/units/partials/_create.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/units/create.html"
    form_class = CustomerWialonUnitCreationForm
    success_url = reverse_lazy("tracker:units")

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        if self.request.GET.get("imei"):
            initial["imei"] = self.request.GET.get("imei")
        return initial

    def form_valid(
        self, form: CustomerWialonUnitCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        new_name = form.cleaned_data["name"]
        imei_number = form.cleaned_data["imei"]
        customer = Customer.objects.get(user=self.request.user)
        with WialonSession() as session:
            unit: WialonUnit | None = wialon_utils.get_unit_by_imei(
                imei=imei_number, session=session
            )
            resource = WialonResource(
                id=customer.wialon_resource_id, session=session
            )
            super_user = WialonUser(id=resource.creator_id, session=session)
            end_user = WialonUser(id=customer.wialon_user_id, session=session)

            if unit is None:
                form.add_error(
                    "imei",
                    ValidationError(
                        _(
                            "Whoops! There aren't any units with IMEI #%(imei_number)s."
                        ),
                        code="invalid",
                        params={"imei_number": imei_number},
                    ),
                )
                return self.form_invalid(form=form)

            super_user.grant_access(
                unit, access_mask=wialon_constants.ACCESSMASK_UNIT_MIGRATION
            )
            end_user.grant_access(
                unit, access_mask=wialon_constants.ACCESSMASK_UNIT_BASIC
            )
            unit.rename(new_name)
            resource.migrate_unit(unit)
            CustomerWialonUnit.objects.create(
                id=unit.id,
                name=unit.name,
                imei=unit.imei_number,
                customer=customer,
            )
        return super().form_valid(form=form)


class CustomerTransactionListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Transaction List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/partials/_transaction_list.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/transaction_list.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["transaction_list"] = self.get_transaction_list()
        return context

    def get_transaction_list(self) -> list[dict[str, typing.Any]]:
        """Returns a list of transactions for the customer's subscription."""
        customer = Customer.objects.get(user=self.request.user)
        return customer.subscription.authorizenet_get_transactions()


class CustomerPaymentMethodListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "payment_list"
    extra_context = {"title": "Payment Method List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    ordering = "id"
    partial_template_name = "terminusgps_tracker/payments/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/payments/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(user=request.user)
        customer.authorizenet_sync_payment_profiles()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            CustomerPaymentMethod.objects.filter(
                customer__user=self.request.user
            )
            .select_related("customer")
            .order_by(self.get_ordering())
        )


class CustomerPaymentMethodDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "payment"
    extra_context = {"title": "Payment Method Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerPaymentMethod
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = CustomerPaymentMethod.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/payments/detail.html"

    def get_queryset(self):
        return CustomerPaymentMethod.objects.filter(
            customer__user=self.request.user
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["paymentProfile"] = (
            self.get_object()
            .authorizenet_get_profile()
            .find(f"{ANET_XML_NS}paymentProfile")
        )
        return context


class CustomerShippingAddressListView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    allow_empty = True
    content_type = "text/html"
    context_object_name = "address_list"
    extra_context = {"title": "Shipping Address List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    ordering = "id"
    partial_template_name = "terminusgps_tracker/addresses/partials/_list.html"
    permission_denied_message = "Please login to view this content."
    queryset = CustomerShippingAddress.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/list.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(user=request.user)
        customer.authorizenet_sync_address_profiles()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        ).order_by(self.get_ordering())


class CustomerShippingAddressDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "address"
    extra_context = {"title": "Shipping Address Details"}
    http_method_names = ["get", "delete"]
    login_url = reverse_lazy("login")
    model = CustomerShippingAddress
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = CustomerShippingAddress.objects.none()
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/detail.html"

    def get_queryset(self):
        return CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        ).select_related("customer")

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["addressProfile"] = (
            self.get_object()
            .authorizenet_get_profile()
            .find(f"{ANET_XML_NS}address")
        )
        return context


class CustomerShippingAddressCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Shipping Address"}
    form_class = CustomerShippingAddressCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/create.html"
    success_url = reverse_lazy("tracker:account")

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerShippingAddressCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer = Customer.objects.get(user=self.request.user)
            address = generate_customer_address(form)
            address_profile = AddressProfile(
                customer_profile_id=customer.authorizenet_profile_id,
                default=form.cleaned_data["default"],
            )
            CustomerShippingAddress.objects.create(
                id=address_profile.create(address), customer=customer
            )
        except AuthorizenetControllerExecutionError as e:
            message = _("Whoops! '%(error)s'")
            if e.code == "E00039":
                message = _("Whoops! This address already exists.")
            form.add_error(
                None, ValidationError(message, code="invalid", params={"e": e})
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class CustomerPaymentMethodCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Payment Method"}
    form_class = CustomerPaymentMethodCreationForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/payments/create.html"
    success_url = reverse_lazy("tracker:account")

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["first_name"] = self.request.user.first_name
        initial["last_name"] = self.request.user.last_name
        return initial

    @transaction.atomic
    def form_valid(
        self, form: CustomerPaymentMethodCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer = Customer.objects.get(user=self.request.user)
            address = generate_customer_address(form)
            payment = generate_customer_payment(form)
            payment_profile = PaymentProfile(
                customer_profile_id=customer.authorizenet_profile_id,
                default=form.cleaned_data["default"],
            )
            CustomerPaymentMethod.objects.create(
                id=payment_profile.create(address=address, payment=payment),
                customer=customer,
            )
            if form.cleaned_data["create_shipping_address"]:
                address_profile = AddressProfile(
                    customer_profile_id=customer.authorizenet_profile_id,
                    default=form.cleaned_data["default"],
                )
                CustomerShippingAddress.objects.create(
                    id=address_profile.create(address), customer=customer
                )
        except AuthorizenetControllerExecutionError as e:
            message = _("Whoops! '%(error)s'")
            if e.code == "E00039":
                message = _(
                    "Whoops! The payment method or shipping address already exists."
                )
            form.add_error(
                None, ValidationError(message, code="invalid", params={"e": e})
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)
