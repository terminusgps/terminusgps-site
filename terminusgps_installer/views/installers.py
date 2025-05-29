from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin


class InstallerDashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard", "subtitle": "Manage your install jobs"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_installer/partials/_dashboard.html"
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_installer/dashboard.html"
