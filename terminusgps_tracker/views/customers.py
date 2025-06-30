import typing

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.models import Customer, Subscription
from terminusgps_tracker.views.mixins import CustomerOrStaffRequiredMixin


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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["customer"] = Customer.objects.get(user=self.request.user)
            return context
        except Customer.DoesNotExist:
            context["customer"] = None
            return context


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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["customer"] = Customer.objects.get(user=self.request.user)
            context["subscription"] = Subscription.objects.get(
                customer=customer
            )
            return context
        except Subscription.DoesNotExist:
            context["subscription"] = None
            return context


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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["customer"] = Customer.objects.get(user=self.request.user)
            return context
        except Customer.DoesNotExist:
            context["customer"] = None
            return context


class CustomerPaymentMethodChoicesView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    extra_context = {"title": "Payment Method Choices"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = Customer
    partial_template_name = (
        "terminusgps_tracker/payments/partials/_choices.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "customer_pk"
    raise_exception = False
    template_name = "terminusgps_tracker/payments/choices.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer = self.get_object()
        if customer is not None:
            context["class"] = settings.DEFAULT_FIELD_CLASS
            context["choices"] = customer.generate_payment_method_choices()
        return context


class CustomerShippingAddressChoicesView(
    LoginRequiredMixin,
    CustomerOrStaffRequiredMixin,
    HtmxTemplateResponseMixin,
    DetailView,
):
    content_type = "text/html"
    extra_context = {"title": "Shipping Address Choices"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = Customer
    partial_template_name = (
        "terminusgps_tracker/addresses/partials/_choices.html"
    )
    permission_denied_message = "Please login to view this content."
    pk_url_kwarg = "customer_pk"
    raise_exception = False
    template_name = "terminusgps_tracker/addresses/choices.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer = self.get_object()
        if customer is not None:
            context["class"] = settings.DEFAULT_FIELD_CLASS
            context["choices"] = customer.generate_shipping_address_choices()
        return context
