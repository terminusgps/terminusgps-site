from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import (
    PasswordChangeView as PasswordChangeViewBase,
)
from django.contrib.auth.views import (
    PasswordResetCompleteView as PasswordResetCompleteViewBase,
)
from django.contrib.auth.views import (
    PasswordResetConfirmView as PasswordResetConfirmViewBase,
)
from django.contrib.auth.views import (
    PasswordResetDoneView as PasswordResetDoneViewBase,
)
from django.contrib.auth.views import (
    PasswordResetView as PasswordResetViewBase,
)
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError

from terminusgps_manager.models import (
    TerminusGPSCustomer,
    WialonResource,
    WialonUser,
)

from ..forms import (
    TerminusgpsAuthenticationForm,
    TerminusgpsPasswordChangeForm,
    TerminusgpsPasswordResetForm,
    TerminusgpsPasswordSetForm,
    TerminusgpsRegistrationForm,
)


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
        # Create resource/account
        super_user = WialonUser()
        super_user.crt = settings.WIALON_ADMIN_ID
        super_user.name = f"super_{form.cleaned_data['username']}"
        super_user.save(push=False)
        resource = WialonResource()
        resource.crt = super_user.pk
        resource.name = f"account_{form.cleaned_data['username']}"
        resource.save(push=False)

        # Create user
        end_user = WialonUser()
        end_user.crt = settings.WIALON_ADMIN_ID
        end_user.name = form.cleaned_data["username"]
        end_user.save(push=False)

        # Assign to customer
        customer.wialon_user = end_user
        customer.wialon_resource = resource
        customer.save(update_fields=["wialon_user", "wialon_resource"])


class PasswordChangeView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, PasswordChangeViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Change"}
    form_class = TerminusgpsPasswordChangeForm
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("password change success")
    template_name = "terminusgps/password_change.html"


class PasswordChangeSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, PasswordChangeDoneView
):
    content_type = "text/html"
    extra_context = {"title": "Password Change Success"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_change_done.html"


class PasswordResetView(HtmxTemplateResponseMixin, PasswordResetViewBase):
    content_type = "text/html"
    email_template_name = "terminusgps/emails/password_reset.txt"
    extra_context = {"title": "Password Reset"}
    form_class = TerminusgpsPasswordResetForm
    http_method_names = ["get", "post"]
    subject_template_name = "terminusgps/emails/password_reset_subject.txt"
    success_url = reverse_lazy("password reset done")
    template_name = "terminusgps/password_reset.html"


class PasswordResetDoneView(
    HtmxTemplateResponseMixin, PasswordResetDoneViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Reset Done"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_done.html"


class PasswordResetConfirmView(
    HtmxTemplateResponseMixin, PasswordResetConfirmViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Reset Confirm"}
    form_class = TerminusgpsPasswordSetForm
    http_method_names = ["get", "post"]
    post_reset_login = True
    success_url = reverse_lazy("password reset complete")
    template_name = "terminusgps/password_reset_confirm.html"


class PasswordResetCompleteView(
    HtmxTemplateResponseMixin, PasswordResetCompleteViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Reset Complete"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_complete.html"
