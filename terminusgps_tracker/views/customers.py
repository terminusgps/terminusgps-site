import typing

from django.contrib.auth.mixins import LoginRequiredMixin
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

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Account"}
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
        context["subtitle"] = (
            f"{self.request.user.first_name}'s account at a glance"
        )
        return context


class CustomerSubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Subscription",
        "subtitle": "Modify your subscription",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/customers/partials/_subscription.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/customers/subscription.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerUnitsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Units", "subtitle": "Modify your units"}
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
        return context


class CustomerTodoView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/customers/partials/_todo.html"
    template_name = "terminusgps_tracker/customers/todo.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer: Customer = Customer.objects.select_related(
            "addresses", "payments", "units"
        ).get(user=self.request.user)
        context["todo_list"] = self.generate_customer_todo_list(customer)
        return context

    def generate_customer_todo_list(
        self, customer: Customer
    ) -> list[dict[str, str]]:
        todo_list: list[dict[str, str]] = []
        if customer.units.count() == 0:
            todo_list.append(
                {
                    "message": "Register your first unit",
                    "link": reverse("tracker:create unit"),
                }
            )
        if customer.addresses.count() == 0:
            todo_list.append(
                {
                    "message": "Add a shipping address",
                    "link": reverse("tracker:create address"),
                }
            )
        if customer.payments.count() == 0:
            todo_list.append(
                {
                    "message": "Add a payment method",
                    "link": reverse("tracker:create payment"),
                }
            )
        if not customer.subscription.exists():
            todo_list.append(
                {
                    "message": "Subscribe!",
                    "link": reverse("tracker:subscription"),
                }
            )
        return todo_list
