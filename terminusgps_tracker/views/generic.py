from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView

from terminusgps_tracker.models import Customer, Subscription
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
)


class TrackerAboutView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_about.html"
    template_name = "terminusgps_tracker/about.html"
    extra_context = {"title": "About", "class": "flex flex-col gap-4"}


class TrackerContactView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_contact.html"
    template_name = "terminusgps_tracker/contact.html"
    extra_context = {"title": "Contact", "class": "flex flex-col gap-4"}


class TrackerPrivacyPolicyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_privacy.html"
    template_name = "terminusgps_tracker/privacy.html"
    extra_context = {"title": "Privacy Policy", "class": "flex flex-col gap-4"}


class TrackerFrequentlyAskedQuestionsView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_faq.html"
    template_name = "terminusgps_tracker/faq.html"
    extra_context = {
        "title": "Frequently Asked Questions",
        "class": "flex flex-col gap-4",
    }


class TrackerSourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG["REPOSITORY_URL"]


class TrackerSettingsView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Settings", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_settings.html"
    template_name = "terminusgps_tracker/settings.html"


class TrackerDashboardView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": "Check out the Terminus GPS mobile app!",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_dashboard.html"
    permission_denied_message = "Please login and try again."
    raise_exception = False
    template_name = "terminusgps_tracker/dashboard.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.customer, _ = Customer.objects.get_or_create(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        context["assets"] = self.customer.assets.all()
        context["subscription"], _ = Subscription.objects.get_or_create(
            customer=self.customer
        )
        return context
