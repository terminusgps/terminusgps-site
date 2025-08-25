import typing

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.models import Customer


class CustomerDashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/customers/partials/_dashboard.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/customers/dashboard.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(user=self.request.user)
        if customer.units.count() == 0:
            messages.add_message(
                request,
                messages.WARNING,
                f"You don't have any units registered! Click <a class='decoration text-terminus-red-800 underline decoration-terminus-black underline-offset-4 hover:text-terminus-red-500 hover:decoration-dotted dark:text-terminus-red-400 dark:decoration-white dark:hover:text-terminus-red-200' href='{reverse('tracker:units')}'>here</a> to add one.",
            )
        if customer.payments.count() == 0:
            messages.add_message(
                request,
                messages.WARNING,
                f"You don't have any payment methods! Click <a class='decoration text-terminus-red-800 underline decoration-terminus-black underline-offset-4 hover:text-terminus-red-500 hover:decoration-dotted dark:text-terminus-red-400 dark:decoration-white dark:hover:text-terminus-red-200' href='{reverse('tracker:create payment')}'>here</a> to add one.",
            )
        if customer.payments.count() == 0:
            messages.add_message(
                request,
                messages.WARNING,
                f"You don't have any shipping addresses! Click <a class='decoration text-terminus-red-800 underline decoration-terminus-black underline-offset-4 hover:text-terminus-red-500 hover:decoration-dotted dark:text-terminus-red-400 dark:decoration-white dark:hover:text-terminus-red-200' href='{reverse('tracker:create address')}'>here</a> to add one.",
            )
        if not customer.is_subscribed:
            messages.add_message(
                request,
                messages.WARNING,
                f"You aren't subscribed yet! Click <a class='decoration text-terminus-red-800 underline decoration-terminus-black underline-offset-4 hover:text-terminus-red-500 hover:decoration-dotted dark:text-terminus-red-400 dark:decoration-white dark:hover:text-terminus-red-200' href='{reverse('tracker:subscription')}'>here</a> to subscribe.",
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"subtitle": "Modify your payment information"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/customers/partials/_account.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/customers/account.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        context["title"] = f"{self.request.user.first_name}'s Account"
        return context


class CustomerSubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"subtitle": "Modify your subscription"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/customers/partials/_subscription.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/customers/subscription.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        customer = Customer.objects.get(user=self.request.user)
        if customer.payments.count() == 0:
            messages.add_message(
                request, messages.WARNING, "Please add a payment method"
            )
        if customer.addresses.count() == 0:
            messages.add_message(
                request, messages.WARNING, "Please add a shipping address"
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        context["title"] = (
            f"{context['customer'].user.first_name}'s Subscription"
        )
        return context


class CustomerUnitsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"subtitle": "Modify your Terminus GPS units"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/customers/partials/_units.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/customers/units.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        context["title"] = f"{context['customer'].user.first_name}'s Units"
        return context
