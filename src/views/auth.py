from django.conf import settings
from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps.wialon.utils import generate_wialon_password

from terminusgps_manager.models import (
    TerminusGPSCustomer,
    WialonAccount,
    WialonUser,
)

from ..forms import TerminusgpsAuthenticationForm, TerminusgpsRegistrationForm


class LoginView(HtmxTemplateResponseMixin, LoginViewBase):
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
    }
    form_class = TerminusgpsAuthenticationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps/login.html"


class LogoutView(HtmxTemplateResponseMixin, LogoutViewBase):
    content_type = "text/html"
    extra_context = {
        "title": "Logged Out",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps/logged_out.html"


class RegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegistrationForm
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("login")
    template_name = "terminusgps/register.html"

    @transaction.atomic
    def form_valid(self, form: TerminusgpsRegistrationForm) -> HttpResponse:
        try:
            user = form.save(commit=True)
            user.email = form.cleaned_data["username"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save(update_fields=["email", "first_name", "last_name"])
            customer = TerminusGPSCustomer()
            customer.user = user
            customer.save(update_fields=["user"])
            self.wialon_registration_flow(form, customer)
            return super().form_valid(form=form)
        except WialonAPIError as error:
            form.add_error(None, ValidationError(str(error), code="invalid"))
            return self.form_invalid(form=form)

    @staticmethod
    @transaction.atomic
    def wialon_registration_flow(
        form: TerminusgpsRegistrationForm, customer: TerminusGPSCustomer
    ) -> None:
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            # Create account user
            super_user_data = session.wialon_api.core_create_user(
                **{
                    "creatorId": settings.WIALON_ADMIN_ID,
                    "name": f"super_{form.cleaned_data['username']}",
                    "password": generate_wialon_password(),
                    "dataFlags": 1,
                }
            )
            super_user = WialonUser()
            super_user.pk = int(super_user_data["item"]["id"])
            super_user.save()

            # Create account resource
            resource_data = session.wialon_api.core_create_resource(
                **{
                    "creatorId": super_user.pk,
                    "name": f"account_{form.cleaned_data['username']}",
                    "skipCreatorCheck": int(True),
                    "dataFlags": 1,
                }
            )
            # Create account from resource
            session.wialon_api.account_create_account(
                **{
                    "itemId": int(resource_data["item"]["pk"]),
                    "plan": "terminusgps_ext_hist",
                }
            )
            session.wialon_api.account_enable_account(
                **{
                    "itemId": int(resource_data["item"]["pk"]),
                    "enable": int(False),
                }
            )
            account = WialonAccount()
            account.pk = int(resource_data["item"]["pk"])
            account.save()

            # Create end user
            end_user_data = session.wialon_api.core_create_user(
                **{
                    "creatorId": settings.WIALON_ADMIN_ID,
                    "name": form.cleaned_data["username"],
                    "password": form.cleaned_data["password1"],
                    "dataFlags": 1,
                }
            )
            end_user = WialonUser()
            end_user.pk = int(end_user_data["item"]["pk"])
            end_user.save()

            # Assign to objects to customer
            customer.wialon_user = end_user
            customer.wialon_account = account
            customer.save(update_fields=["wialon_user", "wialon_account"])
