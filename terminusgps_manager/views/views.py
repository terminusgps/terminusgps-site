import logging
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
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

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.cprofile, _ = CustomerProfile.objects.get_or_create(
            user=request.user
        )
        self.customer, _ = TerminusGPSCustomer.objects.get_or_create(
            user=request.user
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["customerprofile"] = self.cprofile
        return context


class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_manager/dashboard.html"
    extra_context = {"title": "Dashboard"}

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        try:
            context: dict[str, typing.Any] = super().get_context_data(**kwargs)
            context["customer"] = TerminusGPSCustomer.objects.get(
                user=self.request.user
            )
            return context
        except TerminusGPSCustomer.DoesNotExist:
            context["customer"] = None
            return context
