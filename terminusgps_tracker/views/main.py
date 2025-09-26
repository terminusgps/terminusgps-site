from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import SubscriptionCreationForm


class CustomerDashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_dashboard.html"
    template_name = "terminusgps_tracker/dashboard.html"


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Account",
        "subtitle": "Your Terminus GPS account at a glance",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_account.html"
    template_name = "terminusgps_tracker/account.html"


class CustomerUnitsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Units",
        "subtitle": "Your Terminus GPS units and what you can do with them",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_units.html"
    template_name = "terminusgps_tracker/units.html"


class CustomerSubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Your Subscription"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_subscription.html"
    template_name = "terminusgps_tracker/subscription.html"


class CustomerSubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Subscription"}
    form_class = SubscriptionCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/partials/_create_subscription.html"
    )
    template_name = "terminusgps_tracker/create_subscription.html"
    success_url = reverse_lazy("terminusgps_tracker:subscription")
