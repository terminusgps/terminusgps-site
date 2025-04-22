from typing import Any

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from PIL import Image
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.django.utils import scan_barcode

from .forms import VinNumberScanningForm, WialonAssetCreateForm, WialonAssetUpdateForm
from .models import Installer, WialonAsset


class InstallLoginRequiredMixin(LoginRequiredMixin):
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login in order to view this."
    raise_exception = False


class InstallDashboardView(
    InstallLoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_install/partials/_dashboard.html"
    template_name = "terminusgps_install/dashboard.html"


class InstallScanVinNumberView(
    InstallLoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Scan VIN #", "class": "flex flex-col gap-4"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_install/scan_vin.html"
    partial_template_name = "terminusgps_install/partials/_scan_vin.html"
    form_class = VinNumberScanningForm
    success_url = reverse_lazy("install:scan vin success")

    def get_success_url(self, vin_number: str | None = None) -> str:
        if vin_number is not None:
            return f"{self.success_url}?vin={vin_number}"
        return self.success_url

    def form_valid(
        self, form: VinNumberScanningForm
    ) -> HttpResponse | HttpResponseRedirect:
        img = Image.open(form.cleaned_data["image"].file)
        results = scan_barcode(img)
        if not results:
            form.add_error(
                "image",
                ValidationError(
                    _(
                        "Whoops! No barcode was detected in the uploaded image. Please upload a new image."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        extracted_vin: str = results[0].data.decode("utf-8")
        return HttpResponseRedirect(self.get_success_url(extracted_vin))


class InstallScanVinNumberSuccessView(
    InstallLoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Vin # Scanned", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    template_name = "terminusgps_install/scan_vin_success.html"
    partial_template_name = "terminusgps_install/partials/_scan_vin_success.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["vin_number"] = self.request.GET.get("vin", "")
        return context


class InstallAssetCreateView(
    InstallLoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Add Asset", "class": "flex flex-col gap-4"}
    form_class = WialonAssetCreateForm
    http_method_names = ["get", "post"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_create.html"
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_install/assets/create.html"

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["vin_number"] = self.request.GET.get("vin")
        return initial

    def get_form(self, form_class: forms.ModelForm | None = None) -> forms.ModelForm:
        """Updates the form with the installer's allowed accounts."""

        accounts = Installer.objects.get(user=self.request.user).accounts

        form: forms.ModelForm = super().get_form(form_class=form_class)
        form.fields["account"].choices = accounts.order_by("name").values_list(
            "pk", "name"
        )
        return form


class InstallAssetDetailView(
    InstallLoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {"title": "Asset Details"}
    http_method_names = ["get"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_detail.html"
    template_name = "terminusgps_install/assets/detail.html"


class InstallAssetUpdateView(
    InstallLoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    extra_context = {"title": "Update Asset"}
    form_class = WialonAssetUpdateForm
    http_method_names = ["get", "post"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_update.html"
    template_name = "terminusgps_install/assets/update.html"


class InstallAssetListView(
    InstallLoginRequiredMixin, HtmxTemplateResponseMixin, ListView
):
    content_type = "text/html"
    extra_context = {"title": "Asset List"}
    http_method_names = ["get"]
    model = WialonAsset
    partial_template_name = "terminusgps_install/assets/partials/_list.html"
    template_name = "terminusgps_install/assets/list.html"
