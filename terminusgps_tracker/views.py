import requests
from typing import Any
from urllib.parse import urlencode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView

from wialon.api import WialonError
from terminusgps_tracker.forms import (
    TerminusPasswordResetForm,
    TerminusRegistrationForm,
    TerminusLoginForm,
    AssetUploadForm,
    CreditCardUploadForm,
)
from terminusgps_tracker.models.customer import CustomerProfile
from terminusgps_tracker.wialonapi.items import WialonUnit, WialonUnitGroup
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.utils import get_id_from_iccid


class TerminusLoginView(LoginView):
    authentication_form = TerminusLoginForm
    content_type = "text/html"
    extra_context = {"title": "Login"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("profile")
    partial_template_name = "terminusgps_tracker/partials/_login.html"
    template_name = "terminusgps_tracker/login.html"

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if not self.request.headers.get("HX-Request"):
            return super().render_to_response(context, **response_kwargs)
        return self.response_class(
            request=self.request,
            template=self.partial_template_name,
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )


class TerminusLogoutView(LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_logout.html"
    success_url = reverse_lazy("login")
    template_name = "terminusgps_tracker/logout.html"


class TerminusRegistrationView(FormView):
    form_class = TerminusRegistrationForm
    content_type = "text/html"
    extra_context = {
        "title": "Registration",
        "subtitle": "Start tracking your vehicles with the Terminus GPS Tracker",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/register.html"
    partial_template_name = "terminusgps_tracker/partials/_register.html"
    success_url = reverse_lazy("login")

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if self.request.headers.get("HX-Request"):
            return self.response_class(
                request=self.request,
                template=self.partial_template_name,
                context=context,
                using=self.template_engine,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)

    def get_user(self, form: TerminusRegistrationForm) -> AbstractBaseUser:
        user, created = get_user_model().objects.get_or_create(
            username=form.cleaned_data["username"]
        )
        if created:
            user.set_password(form.cleaned_data["password1"])
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()
        return user

    def get_profile(self, user: AbstractBaseUser) -> CustomerProfile:
        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        return profile

    def form_valid(self, form: TerminusRegistrationForm) -> HttpResponse:
        profile = self.get_profile(user=self.get_user(form=form))
        try:
            self.wialon_registration_flow(form=form, profile=profile)
        except WialonError:
            form.add_error(
                "username",
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end. Please try again later."
                    )
                ),
            )
        return super().form_valid(form=form)

    def wialon_registration_flow(
        self, form: TerminusRegistrationForm, profile: CustomerProfile
    ) -> None:
        with WialonSession() as session:
            # Retrieved
            wialon_admin_user = WialonUser(id="27881459", session=session)

            # Created
            wialon_super_user = WialonUser(
                owner=wialon_admin_user,
                name=f"super_{form.cleaned_data["username"]}",
                password=form.cleaned_data["password1"],
                session=session,
            )
            # Created
            wialon_end_user = WialonUser(
                owner=wialon_super_user,
                name=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                session=session,
            )
            # Created
            wialon_group = WialonUnitGroup(
                owner=wialon_super_user,
                name=f"{form.cleaned_data["username"]}'s Group",
                session=session,
            )
            # Created
            wialon_resource = WialonResource(
                owner=wialon_super_user,
                name=f"{form.cleaned_data["username"]} Resource",
                session=session,
            )
            wialon_group.grant_access(user=wialon_end_user)
            profile.wialon_super_user_id = wialon_super_user.id
            profile.wialon_user_id = wialon_end_user.id
            profile.wialon_group_id = wialon_group.id
            profile.wialon_resource_id = wialon_resource.id
            profile.save()


class TerminusPasswordResetView(PasswordResetView):
    form_class = TerminusPasswordResetForm
    content_type = "text/html"
    email_template_name = "terminusgps/emails/password_reset_email.html"
    extra_context = {"title": "Password Reset"}
    extra_email_context = {"subject": "Terminus GPS Password Reset"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/password_reset.html"
    success_url = reverse_lazy("login")


class TerminusProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile.html"
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def get_profile(self) -> CustomerProfile | None:
        return CustomerProfile.objects.get(user=self.request.user) or None

    def get_title(self) -> str:
        return f"{self.request.user.username}'s Profile"

    def get_wialon_items(self) -> list[str]:
        profile = self.get_profile()
        wialon_items: list[str] = []
        if profile and profile.wialon_group_id:
            with WialonSession() as session:
                group = WialonUnitGroup(
                    id=str(profile.wialon_group_id), session=session
                )
                wialon_items.extend(group.items)
        return wialon_items

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        wialon_items = self.get_wialon_items()

        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        context["profile"] = self.get_profile()
        context["wialon_items"] = wialon_items
        context["num_wialon_items"] = len(wialon_items)
        return context


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
