from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from terminusgps.mixins import HtmxTemplateResponseMixin

from .forms import WialonAssetCreateForm, WialonAssetUpdateForm
from .models import WialonAsset


class UserIsStaffTestMixin(UserPassesTestMixin):
    login_url = reverse_lazy("login")
    permission_denied_message = "You must be staff in order to view this."
    raise_exception = False

    def test_func(self) -> bool:
        return self.request.user.is_staff


class InstallDashboardView(
    UserIsStaffTestMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_install/partials/_dashboard.html"
    template_name = "terminusgps_install/dashboard.html"


class InstallAssetCreateView(UserIsStaffTestMixin, HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Add Asset"}
    form_class = WialonAssetCreateForm
    http_method_names = ["get", "post"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_create.html"
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_install/assets/create.html"


class InstallAssetDetailView(
    UserIsStaffTestMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Asset Details"}
    http_method_names = ["get"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_detail.html"
    template_name = "terminusgps_install/assets/detail.html"


class InstallAssetUpdateView(
    UserIsStaffTestMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    extra_context = {"title": "Update Asset"}
    form_class = WialonAssetUpdateForm
    http_method_names = ["get", "post"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_update.html"
    template_name = "terminusgps_install/assets/update.html"


class InstallAssetListView(UserIsStaffTestMixin, HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    extra_context = {"title": "Asset List"}
    http_method_names = ["get"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_list.html"
    template_name = "terminusgps_install/assets/list.html"
