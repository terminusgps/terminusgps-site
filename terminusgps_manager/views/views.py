import logging
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import CustomerProfile

from ..models import TerminusGPSCustomer

logger = logging.getLogger(__name__)


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
    extra_context = {
        "title": "Dashboard",
        "subtitle": "Your Terminus GPS account at a glance",
    }
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
    extra_context = {
        "title": "Units",
        "subtitle": "Your Terminus GPS units at a glance",
    }
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
