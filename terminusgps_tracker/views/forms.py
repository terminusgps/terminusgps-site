import requests
from typing import Any
from urllib.parse import urlencode

from django.views.generic import FormView, TemplateView
from terminusgps_tracker.forms import CreditCardUploadForm, AssetUploadForm
from terminusgps_tracker.http import HttpRequest, HttpResponse
from terminusgps_tracker.integrations.wialon.session import WialonSession


class AddressDropdownView(TemplateView):
    template_name = "terminusgps_tracker/forms/address_dropdown.html"
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.results = None
        self.fill_url = request.build_absolute_uri() or None

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        address = {
            "street": request.GET.get("address_street"),
            "city": request.GET.get("address_city"),
            "state": request.GET.get("address_state"),
            "country": request.GET.get("address_country"),
            "zip": request.GET.get("address_zip"),
        }
        params = self.generate_params(address)
        self.results = self.search_wialon(params)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        print(request.POST)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["fill_url"] = self.fill_url
        context["results"] = self.results
        return context

    def generate_params(
        self, address: dict[str, str | None], count: int = 8
    ) -> dict[str, str]:
        params = {}
        if address.get("street"):
            params.update({"street": address["street"]})
        if address.get("city"):
            params.update({"city": address["city"]})
        if address.get("state") and not address.get("zip"):
            params.update({"region": address["state"]})
        if address.get("state") and address.get("zip"):
            params.update({"region": f"{address["state"]} {address["zip"]}"})
        if address.get("country"):
            params.update({"country": address["country"]})
        params.update(
            {
                "flags": str(sum([0x3, 0x100, 0x200, 0x400])),
                "count": str(count),
                "indexFrom": str(0),
            }
        )
        return params

    def search_wialon(self, params: dict[str, str]) -> dict[str, Any]:
        print(f"Searching Wialon with '{params}'...")
        with WialonSession() as session:
            params.update({"uid": session.uid})
            target_url = (
                "https://search-maps.wialon.com/hst-api.wialon.com/gis_search?"
                + urlencode(params)
            )
            response = requests.post(target_url).json()
            return response[0].get("items")


class CreditCardUploadView(FormView):
    form_class = CreditCardUploadForm
    http_method_names = ["get", "post"]
    extra_context = {"title": "Upload Credit Card"}
    template_name = "terminusgps_tracker/forms/credit_card.html"


class AssetUploadView(FormView):
    form_class = AssetUploadForm
    http_method_names = ["get", "post"]
    extra_context = {
        "title": "Asset Creation",
        "subtitle": "Fill in the IMEI # of your asset and give it a good name",
    }
    template_name = "terminusgps_tracker/forms/asset.html"


class SubscriptionSelectView(FormView): ...
