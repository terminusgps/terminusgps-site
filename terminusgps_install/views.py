from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from terminusgps_install.forms import WialonAssetCreateForm


class InstallDashboardView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    template_name = "terminusgps_install/dashboard.html"
    partial_template_name = "terminusgps_install/partials/_dashboard.html"
    login_url = reverse_lazy("login")
    permission_denied_message = "You do not have permission to view this."
    raise_exception = False


class InstallAssetCreateView(
    PermissionRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Add Asset"}
    form_class = WialonAssetCreateForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_install/assets/partials/_create.html"
    permission_denied_message = "You do not have permission to view this."
    raise_exception = False
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_install/assets/create.html"
    permission_required = "terminusgps_install.add_wialonasset"


class InstallAssetDetailView(LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    extra_context = {"title": "Asset Details"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_install/assets/partials/_detail.html"
    permission_denied_message = "You do not have permission to view this."
    raise_exception = False
    template_name = "terminusgps_install/assets/detail.html"


class InstallAssetUpdateView(LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView):
    content_type = "text/html"
    extra_context = {"title": "Update Asset"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_install/assets/partials/_update.html"
    permission_denied_message = "You do not have permission to view this."
    raise_exception = False
    template_name = "terminusgps_install/assets/update.html"


class InstallAssetListView(LoginRequiredMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    extra_context = {"title": "Asset List"}
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    partial_template_name = "terminusgps_install/assets/partials/_list.html"
    permission_denied_message = "You do not have permission to view this."
    raise_exception = False
    template_name = "terminusgps_install/assets/list.html"
