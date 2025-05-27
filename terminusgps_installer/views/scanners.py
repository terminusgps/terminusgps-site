import typing
import urllib.parse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from PIL import Image
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.django.utils import scan_barcode
from terminusgps.wialon import utils as wialon_utils
from terminusgps.wialon.session import WialonSessionManager

from terminusgps_installer.forms import (
    BarcodeScanForm,
    ImeiNumberConfirmForm,
    VinNumberConfirmForm,
)


class ImeiNumberScanView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Scan IMEI #", "class": "flex flex-col gap-8"}
    form_class = BarcodeScanForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_installer/scanners/partials/_scan_imei.html"
    success_url = reverse_lazy("installer:confirm imei")
    template_name = "terminusgps_installer/scanners/scan_imei.html"

    def form_valid(self, form: BarcodeScanForm) -> HttpResponse | HttpResponseRedirect:
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

        params = {"imei_number": results[0].data.decode("utf-8")}
        return HttpResponseRedirect(self.get_success_url(params))

    def get_success_url(self, params: dict[str, str] | None = None) -> str:
        base_url = super().get_success_url()
        if params:
            return f"{base_url}?{urllib.parse.urlencode(params)}"
        return base_url


class ImeiNumberScanConfirmView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Scanned IMEI #", "class": "flex flex-col gap-8"}
    form_class = ImeiNumberConfirmForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_installer/scanners/partials/_confirm_imei.html"
    template_name = "terminusgps_installer/scanners/confirm_imei.html"

    def get_initial(self, *args, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["imei_number"] = self.request.GET.get("imei_number")
        return initial


class ImeiNumberInfoView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "IMEI # Info", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    template_name = "terminusgps_installer/scanners/info_imei.html"
    partial_template_name = "terminusgps_installer/scanners/partials/_info_imei.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.session_manager = WialonSessionManager(token=settings.WIALON_TOKEN)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        unit = wialon_utils.get_unit_by_imei(
            self.kwargs["imei_number"],
            session=self.session_manager.get_session(sid=None),
        )
        context["info"] = {
            "name": unit.name,
            "id": unit.id,
            "imei": unit.imei_number,
            "pos": unit.get_position(),
        }
        return context


class VinNumberScanView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Scan VIN #", "class": "flex flex-col gap-8"}
    form_class = BarcodeScanForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_installer/scanners/partials/_scan_vin.html"
    success_url = reverse_lazy("installer:confirm vin")
    template_name = "terminusgps_installer/scanners/scan_vin.html"

    def form_valid(self, form: BarcodeScanForm) -> HttpResponse | HttpResponseRedirect:
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

        params = {"vin_number": results[0].data.decode("utf-8")}
        return HttpResponseRedirect(self.get_success_url(params))

    def get_success_url(self, params: dict[str, str] | None = None) -> str:
        base_url = super().get_success_url()

        if params:
            return f"{base_url}?{urllib.parse.urlencode(params)}"
        return base_url


class VinNumberScanConfirmView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Scanned VIN #", "class": "flex flex-col gap-8"}
    form_class = VinNumberConfirmForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_installer/scanners/partials/_confirm_vin.html"
    template_name = "terminusgps_installer/scanners/confirm_vin.html"

    def get_initial(self, *args, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
        initial["vin_number"] = self.request.GET.get("vin_number")
        return initial


class VinNumberInfoView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "VIN # Info", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    template_name = "terminusgps_installer/scanners/info_vin.html"
    partial_template_name = "terminusgps_installer/scanners/partials/_info_vin.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.session_manager = WialonSessionManager(token=settings.WIALON_TOKEN)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        if self.request.GET.get("vin_number"):
            context["info"] = wialon_utils.get_vin_info(
                self.request.GET.get("vin_number", ""),
                session=self.session_manager.get_session(sid=None),
            )
        return context
