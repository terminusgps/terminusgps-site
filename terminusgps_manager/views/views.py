import logging
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import CustomerProfile

from ..models import TerminusGPSCustomer

logger = logging.getLogger(__name__)


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_manager/account.html"
    extra_context = {"title": "Account"}

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"], _ = TerminusGPSCustomer.objects.get_or_create(
            user=self.request.user
        )
        context["customerprofile"], _ = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return context


class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Dashboard"}
    template_name = "terminusgps_manager/dashboard.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"], _ = TerminusGPSCustomer.objects.get_or_create(
            user=self.request.user
        )
        context["customerprofile"], _ = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return context


class UnitsView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Units"}
    template_name = "terminusgps_manager/units.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"], _ = TerminusGPSCustomer.objects.get_or_create(
            user=self.request.user
        )
        context["customerprofile"], _ = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return context


class SubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    extra_context = {"title": "Subscription"}
    template_name = "terminusgps_manager/subscription.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"], _ = TerminusGPSCustomer.objects.get_or_create(
            user=self.request.user
        )
        context["customerprofile"], _ = CustomerProfile.objects.get_or_create(
            user=self.request.user
        )
        return context
