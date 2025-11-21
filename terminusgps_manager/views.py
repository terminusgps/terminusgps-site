import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from . import models


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/partials/_dashboard.html"
    template_name = "terminusgps_manager/dashboard.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Adds :py:attr:`customer` to the view."""
        if hasattr(request, "user"):
            user = getattr(request, "user")
            if user.is_authenticated:
                self.customer = (
                    models.TerminusgpsCustomer.objects.get_or_create(user=user)
                )
            else:
                self.customer = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        """Adds :py:attr:`customer` to the view context."""
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/partials/_account.html"
    template_name = "terminusgps_manager/account.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class SubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Subscription"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/partials/_subscription.html"
    template_name = "terminusgps_manager/subscription.html"
