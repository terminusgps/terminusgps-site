import logging
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from ..models import TerminusGPSCustomer

logger = logging.getLogger(__name__)


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_manager/account.html"
    extra_context = {"title": "Account"}

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = (
            self.customer.customer_profile
            if self.customer is not None
            else None
        )
        return context


class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Dashboard"}
    template_name = "terminusgps_manager/dashboard.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = (
            self.customer.customer_profile
            if self.customer is not None
            else None
        )
        return context


class UnitsView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Units"}
    template_name = "terminusgps_manager/units.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = (
            self.customer.customer_profile
            if self.customer is not None
            else None
        )
        return context


class SubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Subscription"}
    template_name = "terminusgps_manager/subscription.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = (
            self.customer.customer_profile
            if self.customer is not None
            else None
        )
        return context
