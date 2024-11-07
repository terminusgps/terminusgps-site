from django.contrib.auth.mixins import LoginRequiredMixin
import requests
from typing import Any
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from terminusgps_tracker.forms import (
    CreditCardUploadForm,
    AssetUploadForm,
    SubscriptionSelectForm,
)
from terminusgps_tracker.http import HttpRequest, HttpResponse
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.models import TrackerProfile


class SubscriptionSelectView(LoginRequiredMixin, FormView):
    template_name = "terminusgps_tracker/forms/subscription_select.html"
    http_method_names = ["get", "post"]
    form_class = SubscriptionSelectForm
    extra_context = {"title": "Your Subscription"}
    success_url = reverse_lazy("tracker profile")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        context["default_subscription"] = self.profile.subscriptions.all()
        context["subtitle"] = f"You're currently on our {self.profile.user} plan!"
        return context


class AddressDropdownView(TemplateView):
    template_name = "terminusgps_tracker/forms/address_dropdown.html"
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.results = None
        self.fill_url = request.build_absolute_uri() or None

    def post(self, request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        formatted_path = request.POST.get("formatted_path")
        address = self.path_to_dict(formatted_path)
        if not address:
            return HttpResponse(status=401)
        return HttpResponseRedirect(redirect_to=reverse("upload credit card"))

    def path_to_dict(self, formatted_path: str | None = None) -> dict[str, str]:
        address_keys = [
            "address_street",
            "address_city",
            "address_state",
            "address_zip",
            "address_country",
            "address_phone",
        ]
        address_dict = dict(zip(address_keys, [""] * len(address_keys)))
        return address_dict

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        with WialonSession() as session:
            params = self.generate_params(
                address={
                    "street": request.GET.get("address_street"),
                    "city": request.GET.get("address_city"),
                    "state": request.GET.get("address_state"),
                    "country": request.GET.get("address_country"),
                    "zip": request.GET.get("address_zip"),
                },
                count=8,
                session=session,
            )
            self.results = self.search_wialon(params)
            print(self.results)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["fill_url"] = self.fill_url
        context["results"] = self.results
        return context

    def generate_params(
        self, address: dict[str, str | None], session: WialonSession, count: int = 8
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
                "uid": session.uid,
            }
        )
        return params

    def search_wialon(self, params: dict[str, str]) -> list[dict[str, Any]]:
        target_url = (
            "https://search-maps.wialon.com/hst-api.wialon.com/gis_search?"
            + urlencode(params)
        )
        response = requests.post(target_url).json()
        return [item.get("items")[0] for item in response]


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
