from typing import Any

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from wialon.api import WialonError

from terminusgps_tracker.forms import CustomerRegistrationForm, AssetCustomizationForm
from terminusgps_tracker.forms.customer import CustomerAuthenticationForm
from terminusgps_tracker.models import CustomerProfile
from terminusgps_tracker.wialonapi.items.resource import WialonResource
from terminusgps_tracker.wialonapi.items.unit import WialonUnit
from terminusgps_tracker.wialonapi.items.unit_group import WialonUnitGroup
from terminusgps_tracker.wialonapi.items.user import WialonUser
from terminusgps_tracker.wialonapi.session import WialonSession


def form_success_redirect(
    request: HttpRequest, redirect_url: str = "https://hosting.terminusgps.com/"
) -> HttpResponse:
    context = {"title": "Success", "redirect_url": redirect_url}
    return render(
        request, "terminusgps_tracker/forms/form_success.html", context=context
    )


class LoginFormView(LoginView):
    authentication_form = CustomerAuthenticationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_login.html"
    extra_context = {"title": "Login", "client_name": settings.CLIENT_NAME}
    redirect_authenticated_user = False
    success_url = reverse_lazy("dashboard")


class LogoutFormView(LogoutView):
    template_name = "terminusgps_tracker/forms/form_logout.html"
    http_method_names = ["get", "post"]
    extra_context = {"title": "Logout", "client_name": settings.CLIENT_NAME}

    def get_success_url(self) -> str:
        return reverse_lazy("form login")


class RegistrationFormView(FormView):
    form_class = CustomerRegistrationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_registration.html"
    extra_context = {"title": "Registration", "client_name": settings.CLIENT_NAME}
    success_url = reverse_lazy("form asset customization")

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


class AssetCustomizationFormView(LoginRequiredMixin, FormView):
    form_class = AssetCustomizationForm
    http_method_name = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_asset_customization.html"
    login_url = reverse_lazy("form login")
    success_url = reverse_lazy("form success")
    extra_context = {
        "title": "Asset Customization",
        "client_name": settings.CLIENT_NAME,
    }

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["imei"] = self.request.GET.get("imei", None)
        return context

    def form_valid(self, form: AssetCustomizationForm) -> HttpResponse:
        with WialonSession() as session:
            unit_id: str | None = session.get_id_from_iccid(
                iccid=form.cleaned_data["imei_number"]
            )

            if unit_id is not None:
                unit = WialonUnit(id=unit_id, session=session)
                unit.rename(form.cleaned_data["asset_name"])
            else:
                form.add_error(
                    "imei_number",
                    ValidationError(
                        _("Invalid IMEI #: '%(value)s'. Please try a different value."),
                        params={"value": form.cleaned_data["imei_number"]},
                        code="invalid",
                    ),
                )
        return super().form_valid(form=form)
