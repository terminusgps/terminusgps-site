from django.views.generic import TemplateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_installer.views.mixins import InstallerRequiredMixin


class InstallerDashboardView(
    InstallerRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard", "subtitle": "Manage your install jobs"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_installer/partials/_dashboard.html"
    template_name = "terminusgps_installer/dashboard.html"
