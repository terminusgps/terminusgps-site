from authorizenet.apicontractsv1 import customerAddressType
import requests
from typing import Any
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.utils import get_id_from_iccid
from terminusgps_tracker.forms import AssetUploadForm, CreditCardUploadForm
from terminusgps_tracker.wialonapi.items import WialonUnit, WialonUnitGroup
from terminusgps_tracker.authorizenetapi.profiles import AuthorizenetProfile
from terminusgps_tracker.models import CustomerProfile


class FormSuccessView(TemplateView):
    template_name = "terminusgps_tracker/forms/success.html"
    content_type = "text/html"
    http_method_names = ["get"]
    redirect_url = reverse_lazy("profile")
    extra_context = {"title": "Success!"}

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["redirect_url"] = self.redirect_url
        return context


class SearchAddress(TemplateView):
    template_name = "terminusgps_tracker/forms/widgets/address_dropdown.html"
    content_type = "text/html"
    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            phrase = self.get_search_phrase(request)
            raw_results = self.search_address(phrase)
            context: dict[str, Any] = self.get_context_data(**kwargs)
            context["results"] = self.process_search_results(raw_results)
            context["fill_url"] = reverse("upload payment")
            return self.render_to_response(context)
        return super().get(request, *args, **kwargs)

    def search_address(
        self,
        phrase: str,
        count: int = 6,
        index_from: int = 0,
        host: str = "hst-api.wialon.com",
    ) -> list:
        with WialonSession() as session:
            url = f"https://search-maps.wialon.com/{host}/gis_searchintelli?"
            print(f"Searching Wialon with phrase: '{phrase}'...")
            params = urlencode(
                {
                    "phrase": phrase,
                    "count": count,
                    "indexFrom": index_from,
                    "uid": session.uid,
                }
            )
            response: list = requests.post(url + params).json()
            return [item.get("items") for item in response]

    def process_search_results(self, raw_results: list) -> list:
        items = [item[0] for item in raw_results]
        processed_results = []
        for item in items:
            processed_results.append(
                {
                    "city": item.get("city"),
                    "country": item.get("country"),
                    "formatted_path": item.get("formatted_path"),
                    "house": item.get("house"),
                    "map": item.get("map"),
                    "region": item.get("region"),
                    "street": item.get("street"),
                    "lat": item.get("y"),
                    "lon": item.get("x"),
                }
            )
        return processed_results

    def get_search_phrase(self, request: HttpRequest) -> str:
        user_input = {
            "address_street": request.GET.get("address_street"),
            "address_city": request.GET.get("address_city"),
            "address_state": request.GET.get("address_state"),
            "address_zip": request.GET.get("address_zip"),
            "address_country": request.GET.get("address_country"),
        }
        return ", ".join([value.strip() for value in user_input.values() if value])


class CreditCardHelpView(TemplateView):
    extra_context = {"title": "Help Payment Upload"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/forms/help_payment.html"


class AssetHelpView(TemplateView):
    extra_context = {"title": "Help Asset Upload"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/forms/help_asset.html"


class CreditCardUploadView(LoginRequiredMixin, FormView):
    extra_context = {"title": "Upload Payment"}
    form_class = CreditCardUploadForm
    help_url = reverse_lazy("help payment")
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    success_url = "https://hosting.terminusgps.com/"
    template_name = "terminusgps_tracker/forms/payment.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request") and request.GET.get("formatted_path"):
            formatted_path: str | None = request.GET.get("formatted_path")
            address_dict = self.convert_path_to_address(formatted_path)
            form = self.get_form()
            for key, value in address_dict.items():
                form.fields["address"].fields
            return self.render_to_response(context={"form": form})
        else:
            context = self.get_context_data()
            return self.render_to_response(context=context)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["help_url"] = self.help_url
        return context

    def form_valid(self, form: CreditCardUploadForm) -> HttpResponse:
        try:
            self.authorizenet_profile_creation_flow(request=self.request, form=form)
        except ValueError:
            form.add_error(
                "address",
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end. Please try again later."
                    )
                ),
            )
        return super().form_valid(form=form)

    def authorizenet_profile_creation_flow(
        self, request: HttpRequest, form: CreditCardUploadForm
    ) -> None:
        if not request.user.is_authenticated:
            raise ValueError("No authenticated user provided.")

        customer_profile = AuthorizenetProfile(user=request.user)
        billing_address = customerAddressType(
            firstName=request.user.first_name,
            lastName=request.user.last_name,
            address=form.cleaned_data["address_street"],
            city=form.cleaned_data["address_city"],
            state=form.cleaned_data["address_state"],
            zip=form.cleaned_data["address_zip"],
            country=form.cleaned_data["address_country"],
        )
        customer_profile.create_payment_profile(
            billing_address=billing_address,
            card_number=form.cleaned_data["credit_card_number"],
            card_expiry=f"{form.cleaned_data["credit_card_expiry_month"]}-{form.cleaned_data["credit_card_expiry_year"]}",
        )

    def convert_path_to_address(
        self, formatted_path: str | None = None
    ) -> dict[str, str | None]:
        def create_address_dict(address: dict) -> dict[str, str | None]:
            return {
                "address_street": address.get("street"),
                "address_city": address.get("city"),
                "address_state": address.get("state"),
                "address_zip": address.get("zip"),
                "address_country": address.get("country"),
            }

        if formatted_path is None:
            raise ValueError("No formatted path provided.")
        addr_parts = [part.strip() for part in formatted_path.split(",")]
        addr_keys = ["street", "city", "state_zip", "country"]
        address = dict(zip(addr_keys, addr_parts))
        address["state"], address["zip"] = address["state_zip"].split(" ")
        del address["state_zip"]
        return create_address_dict(address)


class AssetUploadView(LoginRequiredMixin, FormView):
    form_class = AssetUploadForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/asset.html"
    extra_context = {"title": "Asset Customization"}
    success_url = reverse_lazy("profile")
    help_url = reverse_lazy("help asset")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["help_url"] = self.help_url
        return context

    def form_valid(self, form: AssetUploadForm) -> HttpResponse:
        form = self.wialon_asset_customization_flow(form)
        if form.is_valid():
            return super().form_valid(form=form)
        else:
            return self.form_invalid(form=form)

    def get_unit(
        self, form: AssetUploadForm, session: WialonSession
    ) -> WialonUnit | None:
        unit_id: str | None = get_id_from_iccid(
            iccid=form.cleaned_data["imei_number"], session=session
        )
        if unit_id:
            return WialonUnit(id=unit_id, session=session)

    def wialon_asset_customization_flow(self, form: AssetUploadForm) -> AssetUploadForm:
        profile = CustomerProfile.objects.get(user=self.request.user)
        with WialonSession() as session:
            unit: WialonUnit | None = self.get_unit(form=form, session=session)
            if unit is not None:
                user_group = WialonUnitGroup(
                    id=str(profile.wialon_group_id), session=session
                )
                available_units = WialonUnitGroup(id="27890571", session=session)
                unit.rename(form.cleaned_data["asset_name"])
                available_units.rm_item(unit)
                user_group.add_item(unit)
                profile.completed_registration = True
                profile.save()
            else:
                form.add_error(
                    "imei_number",
                    ValidationError(
                        _(
                            "Whoops! We couldn't find the asset, please ensure your IMEI # is correctly input."
                        ),
                        code="invalid",
                    ),
                )
        return form
