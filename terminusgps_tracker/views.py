import requests
from typing import Any
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from wialon.api import WialonError

from terminusgps_tracker.models import CustomerProfile
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.utils import get_id_from_iccid
from terminusgps_tracker.forms import (
    CustomerRegistrationForm,
    AssetCustomizationForm,
    CreditCardUploadForm,
)
from terminusgps_tracker.wialonapi.items import (
    WialonResource,
    WialonUnit,
    WialonUnitGroup,
    WialonUser,
)


class SearchAddress(TemplateView):
    template_name = "terminusgps_tracker/forms/widgets/address_dropdown.html"
    content_type = "text/html"
    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=401)
        phrase = self.get_search_phrase(request)
        raw_results = self.search_address(phrase)
        context: dict[str, Any] = self.get_context_data(**kwargs)
        context["results"] = self.process_search_results(raw_results)
        context["form_url"] = reverse("upload credit card")
        return self.render_to_response(context)

    def search_address(
        self,
        phrase: str,
        count: int = 16,
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


class CreditCardUploadView(FormView):
    form_class = CreditCardUploadForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/credit_card_upload.html"
    extra_context = {"title": "Upload Credit Card"}

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if (
            request.headers.get("HX-Request")
            and request.GET.get("formatted_path") is not None
        ):
            formatted_path: str | None = request.GET.get("formatted_path")
            address = self.convert_path_to_address(formatted_path)
            context = self.get_context_data()
            return self.render_to_response(context=context)
        else:
            context = self.get_context_data()
            return self.render_to_response(context=context)

    def convert_path_to_address(
        self, formatted_path: str | None = None
    ) -> dict[str, str]:
        if formatted_path is None:
            raise ValueError("No formatted path provided.")
        addr_parts = [part.strip() for part in formatted_path.split(",")]
        addr_keys = ["street", "city", "state_zip", "country"]
        address = dict(zip(addr_keys, addr_parts))
        address["state"], address["zip"] = address["state_zip"].split(" ")
        del address["state_zip"]
        return address


class CustomerRegistrationView(FormView):
    form_class = CustomerRegistrationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/register.html"
    extra_context = {"title": "Registration"}

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.session.get("imei_number"):
            request.session["imei_number"] = request.GET.get("imei", None)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: CustomerRegistrationForm) -> HttpResponse:
        user = get_user_model().objects.create(
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
        )
        customer_profile = CustomerProfile.objects.create(user=user)
        try:
            self.wialon_registration_flow(form=form, customer_profile=customer_profile)
        except WialonError:
            form.add_error(
                "imei_number",
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end. Please try again later."
                    )
                ),
            )
        return redirect(reverse("asset"))

    def wialon_registration_flow(
        self, form: CustomerRegistrationForm, customer_profile: CustomerProfile
    ) -> None:
        with WialonSession() as session:
            # Retrieved
            wialon_admin_user = WialonUser(id="27881459", session=session)

            # Created
            wialon_super_user = WialonUser(
                owner=wialon_admin_user,
                name=f"super_{form.cleaned_data["email"]}",
                password=form.cleaned_data["password1"],
                session=session,
            )
            # Created
            wialon_end_user = WialonUser(
                owner=wialon_super_user,
                name=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
                session=session,
            )
            # Created
            wialon_group = WialonUnitGroup(
                owner=wialon_super_user,
                name=f"{form.cleaned_data["email"]}'s Group",
                session=session,
            )
            # Created
            wialon_resource = WialonResource(
                owner=wialon_super_user,
                name=f"{form.cleaned_data["email"]} Resource",
                session=session,
            )
            customer_profile.wialon_super_user_id = wialon_super_user.id
            customer_profile.wialon_user_id = wialon_end_user.id
            customer_profile.wialon_group_id = wialon_group.id
            customer_profile.wialon_resource_id = wialon_resource.id
            customer_profile.save()


class AssetCustomizationView(FormView):
    form_class = AssetCustomizationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/asset.html"
    extra_context = {"title": "Asset Customization"}
    success_url = reverse_lazy("form success")

    def get_initial(self) -> dict[str, Any]:
        if self.request.session.get("imei_number"):
            return {"imei_number": self.request.session.get("imei_number")}
        return super().get_initial()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.GET.get("imei") is not None and not request.session["imei_number"]:
            request.session["imei_number"] = request.GET.get("imei", None)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: AssetCustomizationForm) -> HttpResponse:
        form = self.wialon_asset_customization_flow(form)
        if form.is_valid():
            self.request.session.flush()
            return super().form_valid(form=form)
        else:
            return self.form_invalid(form=form)

    def get_unit(
        self, form: AssetCustomizationForm, session: WialonSession
    ) -> WialonUnit | None:
        unit_id: str | None = get_id_from_iccid(
            iccid=form.cleaned_data["imei_number"], session=session
        )
        if unit_id:
            return WialonUnit(id=unit_id, session=session)

    def wialon_asset_customization_flow(
        self, form: AssetCustomizationForm
    ) -> AssetCustomizationForm:
        with WialonSession() as session:
            unit: WialonUnit | None = self.get_unit(form=form, session=session)
            if unit is not None:
                available_units = WialonUnitGroup(id="27890571", session=session)
                unit.rename(form.cleaned_data["asset_name"])
                available_units.rm_item(unit)
            else:
                form.add_error(
                    "imei_number",
                    ValidationError(
                        _(
                            "Whoops! Something went wrong on our end. Please try again later."
                        ),
                        code="invalid",
                    ),
                )
        return form
