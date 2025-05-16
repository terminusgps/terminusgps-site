import typing

from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from PIL import Image
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.django.utils import scan_barcode

from .forms import UnitCreationForm, VinNumberScanForm


class VinNumberScanFormView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Scan VIN #", "class": "flex flex-col gap-8"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_installer/scan_vin.html"
    partial_template_name = "terminusgps_installer/partials/_scan_vin.html"
    form_class = VinNumberScanForm
    success_url = reverse_lazy("installer:scan vin success")

    def form_valid(
        self, form: VinNumberScanForm
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

    def get_success_url(self, vin_number: str | None = None) -> str:
        if vin_number is not None:
            return f"{super().get_success_url()}?vin={vin_number}"
        return super().get_success_url()


class VinNumberScanSuccessView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Scanned VIN #", "class": "flex flex-col gap-8"}
    http_method_names = ["get"]
    template_name = "terminusgps_installer/scan_vin_success.html"
    partial_template_name = "terminusgps_installer/partials/_scan_vin_success.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["vin_number"] = self.request.GET.get("vin", "")
        return context


class UnitCreationFormView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Unit Creation", "class": "flex flex-col gap-8"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_installer/create_unit.html"
    partial_template_name = "terminusgps_installer/partials/_create_unit.html"
    form_class = UnitCreationForm
