from authorizenet.apicontractsv1 import customerAddressType
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView, RedirectURLMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from wialon.api import WialonError

from terminusgps_tracker.authorizenetapi.profiles import AuthorizenetProfile
from terminusgps_tracker.models import CustomerProfile
from terminusgps_tracker.wialonapi.session import WialonSession

from terminusgps_tracker.forms import (
    CustomerAssetCustomizationForm,
    CustomerCreditCardUploadForm,
    CustomerRegistrationForm,
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
    success_url = reverse_lazy("form asset customization")

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.request.session.get("imei_number"):
            self.request.session["imei_number"] = self.request.GET.get("imei", None)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: CustomerRegistrationForm) -> HttpResponse:
        customer_profile = CustomerProfile.objects.create(
            user=User.objects.create_user(
                username=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                password=form.cleaned_data["password1"],
            )
        )
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
        else:
            user = authenticate(
                self.request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password1"],
            )
            login(self.request, user)

        return super().form_valid(form=form)

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


class CustomerAssetCustomizationView(FormView):
    form_class = CustomerAssetCustomizationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_asset_customization.html"
    extra_context = {
        "title": "Asset Customization",
        "client_name": settings.CLIENT_NAME,
    }

    def _get_unit_id(
        self, form: CustomerAssetCustomizationForm, session: WialonSession
    ) -> str | None:
        if self.request.session.get("imei_number") is not None:
            imei_number = self.request.session["imei_number"]
        else:
            imei_number = form.cleaned_data["imei_number"]
        return session.get_id_from_iccid(iccid=imei_number)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.request.session.get("imei_number"):
            self.request.session["imei_number"] = self.request.GET.get("imei", None)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: CustomerAssetCustomizationForm) -> HttpResponse:
        with WialonSession() as session:
            unit_id: str | None = self._get_unit_id(form=form, session=session)
            if unit_id is not None:
                unit = WialonUnit(id=unit_id, session=session)
                unit.rename(form.cleaned_data["asset_name"])
            else:
                form.add_error(
                    "imei_number",
                    ValidationError(
                        _("Invalid IMEI #: '%(value)s'. Please try a different value."),
                        params={
                            "value": self.request.session["imei_number"]
                            or form.cleaned_data["imei_number"]
                        },
                        code="invalid",
                    ),
                )
        return super().form_valid(form=form)


class CustomerCreditCardUploadView(FormView):
    form_class = CustomerCreditCardUploadForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_cc_upload.html"
    login_url = reverse_lazy("form login")
    success_url = reverse_lazy("form success")
    extra_context = {
        "title": "Payment Method Upload",
        "client_name": settings.CLIENT_NAME,
    }

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.request.session.get("imei_number"):
            self.request.session["imei_number"] = self.request.GET.get("imei", None)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form: CustomerCreditCardUploadForm) -> HttpResponse:
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
        return super().form_valid(form=form)
