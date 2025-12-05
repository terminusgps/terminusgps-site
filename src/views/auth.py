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
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView
from terminusgps.mixins import HtmxTemplateResponseMixin

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
    partial_template_name = "terminusgps/partials/_login.html"
    template_name = "terminusgps/login.html"


class LogoutView(HtmxTemplateResponseMixin, LogoutViewBase):
    content_type = "text/html"
    extra_context = {
        "title": "Logged Out",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_logged_out.html"
    template_name = "terminusgps/logged_out.html"


class RegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegistrationForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_register.html"
    success_url = reverse_lazy("login")
    template_name = "terminusgps/register.html"

    @transaction.atomic
    def form_valid(self, form: TerminusgpsRegistrationForm) -> HttpResponse:
        user = form.save(commit=True)
        user.email = form.cleaned_data["username"]
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.save(update_fields=["email", "first_name", "last_name"])
        return super().form_valid(form=form)


class PasswordChangeView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, PasswordChangeViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Change"}
    form_class = TerminusgpsPasswordChangeForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_password_change.html"
    success_url = reverse_lazy("password change success")
    template_name = "terminusgps/password_change.html"


class PasswordChangeSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, PasswordChangeDoneView
):
    content_type = "text/html"
    extra_context = {"title": "Password Change Success"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_password_change_done.html"
    template_name = "terminusgps/password_change_done.html"


class PasswordResetView(HtmxTemplateResponseMixin, PasswordResetViewBase):
    content_type = "text/html"
    email_template_name = "terminusgps/emails/password_reset.txt"
    extra_context = {"title": "Password Reset"}
    form_class = TerminusgpsPasswordResetForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_password_reset.html"
    subject_template_name = "terminusgps/emails/password_reset_subject.txt"
    success_url = reverse_lazy("password reset done")
    template_name = "terminusgps/password_reset.html"


class PasswordResetDoneView(
    HtmxTemplateResponseMixin, PasswordResetDoneViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Reset Done"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_password_reset_done.html"
    template_name = "terminusgps/password_reset_done.html"


class PasswordResetConfirmView(
    HtmxTemplateResponseMixin, PasswordResetConfirmViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Reset Confirm"}
    form_class = TerminusgpsPasswordSetForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_password_reset_confirm.html"
    post_reset_login = True
    success_url = reverse_lazy("password reset complete")
    template_name = "terminusgps/password_reset_confirm.html"


class PasswordResetCompleteView(
    HtmxTemplateResponseMixin, PasswordResetCompleteViewBase
):
    content_type = "text/html"
    extra_context = {"title": "Password Reset Complete"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps/partials/_password_reset_complete.html"
    )
    template_name = "terminusgps/password_reset_complete.html"
