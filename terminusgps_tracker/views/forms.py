from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
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


def form_success_redirect(
    request: HttpRequest, redirect_url: str = "https://hosting.terminusgps.com/"
) -> HttpResponse:
    return render(
        request,
        "terminusgps_tracker/forms/form_success_redirect.html",
        context={"title": "Success!", "redirect_url": redirect_url},
    )


class CustomerLoginView(LoginView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_tracker/forms/form_login.html"


class CustomerLogoutView(LogoutView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("form login")
    template_name = "terminusgps_tracker/forms/form_logout.html"


class CustomerRegistrationView(FormView):
    form_class = CustomerRegistrationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_register.html"
    extra_context = {"title": "Registration", "client_name": settings.CLIENT_NAME}

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

        user = authenticate(
            self.request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)
        return redirect(reverse("form asset customization"))

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
    template_name = "terminusgps_tracker/forms/form_asset_customization.html"
    extra_context = {
        "title": "Asset Customization",
        "client_name": settings.CLIENT_NAME,
    }
    success_url = reverse_lazy("form success")

    def get_initial(self) -> dict[str, Any]:
        if self.request.session.get("imei_number"):
            return {"imei_number": self.request.session.get("imei_number")}
        return super().get_initial()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.GET.get("imei") is not None:
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


class CreditCardUploadView(FormView):
    form_class = CreditCardUploadForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_cc_upload.html"
    login_url = reverse_lazy("form login")
    success_url = reverse_lazy("form success")
    extra_context = {"title": "Credit Card Upload", "client_name": settings.CLIENT_NAME}

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.request.session.get("imei_number"):
            self.request.session["imei_number"] = self.request.GET.get("imei", None)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: CreditCardUploadForm) -> HttpResponse:
        """
        if self.request.user.is_authenticated:
            auth_profile = AuthorizenetProfile(user=self.request.user)
            auth_profile.create_payment_profile(
                billing_address=customerAddressType(
                    firstName=form.cleaned_data["first_name"],
                    lastName=form.cleaned_data["last_name"],
                    address=form.cleaned_data["address_street"],
                    city=form.cleaned_data["address_city"],
                    state=form.cleaned_data["address_state"],
                    zip=form.cleaned_data["address_zip"],
                    country=form.cleaned_data["address_country"],
                    phoneNumber=form.cleaned_data["address_phone"],
                ),
                card_number=form.cleaned_data["cc_number"],
                card_expiry=form.cleaned_data["cc_expiry"],
            )
        """
        return super().form_valid(form=form)
