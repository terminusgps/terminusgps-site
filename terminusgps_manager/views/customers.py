from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from .. import models


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
        self.customer = None
        if hasattr(request, "user") and request.user.is_authenticated:
            self.customer, _ = (
                models.TerminusgpsCustomer.objects.get_or_create(
                    user=request.user
                )
            )
        return super().setup(request, *args, **kwargs)


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/partials/_account.html"
    template_name = "terminusgps_manager/account.html"
