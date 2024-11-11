import requests
from wialon.api import WialonError
from typing import Any
from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from authorizenet.apicontractsv1 import customerAddressType, paymentType, creditCardType
from terminusgps_tracker.forms import CreditCardUploadForm, AssetUploadForm
from terminusgps_tracker.http import HttpRequest, HttpResponse
from terminusgps_tracker.integrations.wialon.items import WialonUnitGroup, WialonUnit
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.utils import get_id_from_iccid
from terminusgps_tracker.models import TrackerProfile
from terminusgps_tracker.models.subscription import TrackerPaymentMethod


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


class CreditCardUploadView(LoginRequiredMixin, FormView):
    form_class = CreditCardUploadForm
    http_method_names = ["get", "post"]
    extra_context = {"title": "Upload Credit Card"}
    template_name = "terminusgps_tracker/forms/credit_card.html"
    login_url = reverse_lazy("tracker login")

    def setup(self, *args, **kwargs) -> None:
        super().setup(*args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=self.request.user) or None

    def form_valid(self, form: CreditCardUploadForm) -> HttpResponse:
        payment = paymentType(
            creditCard=creditCardType(
                cardNumber=form.cleaned_data["credit_card_number"],
                expirationDate=form.cleaned_data["credit_card_expiry_month"]
                + "-"
                + form.cleaned_data["credit_card_expiry_year"],
                cardCode=form.cleaned_data["credit_card_ccv"],
            )
        )
        if self.profile:
            payment_method = TrackerPaymentMethod.objects.create(profile=self.profile)
            billing_address = customerAddressType(
                firstName=self.profile.first_name,
                lastName=self.profile.last_name,
                address=form.cleaned_data["address_street"],
                city=form.cleaned_data["address_city"],
                state=form.cleaned_data["address_state"],
                zip=form.cleaned_data["address_zip"],
                country=form.cleaned_data["address_country"],
            )
            payment_method.save(
                payment=payment, billing_address=billing_address, default=True
            )
        return super().form_valid(form=form)


class AssetUploadView(FormView):
    form_class = AssetUploadForm
    http_method_names = ["get", "post"]
    extra_context = {
        "title": "Asset Creation",
        "subtitle": "Fill in the IMEI # of your asset and give it a good name",
    }
    template_name = "terminusgps_tracker/forms/asset.html"
    success_url = reverse_lazy("tracker profile")

    def setup(self, *args, **kwargs) -> None:
        super().setup(*args, **kwargs)
        try:
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        except TrackerProfile.DoesNotExist:
            self.profile = None

    def get_unit(self, form: AssetUploadForm, session: WialonSession) -> WialonUnit:
        unit_id: str | None = get_id_from_iccid(
            iccid=form.cleaned_data["imei_number"], session=session
        )
        if not unit_id:
            raise ValueError(
                f"Could not locate unit by imei: '{form.cleaned_data["imei_number"]}'"
            )
        return WialonUnit(id=unit_id, session=session)

    def wialon_asset_assignment_flow(self, form: AssetUploadForm) -> None:
        with WialonSession() as session:
            unit = self.get_unit(form, session=session)
            available_group = WialonUnitGroup(id="27890571", session=session)
            user_group = WialonUnitGroup(
                id=str(self.profile.wialon_group_id), session=session
            )

            unit.rename(form.cleaned_data["asset_name"])
            user_group.add_item(unit)
            available_group.rm_item(unit)

    def form_valid(self, form: AssetUploadForm) -> HttpResponse:
        try:
            self.wialon_asset_assignment_flow(form)
        except WialonError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "'%(value)s' cannot be registered at this time. Please try again later!"
                    ),
                    params={"value": form.cleaned_data["imei_number"]},
                ),
            )
            return self.form_invalid(form=form)
        except ValueError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _("'%(value)s' could not be found in the Terminus GPS database."),
                    params={"value": form.cleaned_data["imei_number"]},
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)
