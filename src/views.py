from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from terminusgps.django.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonResource, WialonUser
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.models import Customer

from .forms import TerminusgpsAuthenticationForm, TerminusgpsRegisterForm


class TerminusgpsPasswordResetView(HtmxTemplateResponseMixin, PasswordResetView):
    content_type = "text/html"
    email_template_name = "terminusgps/emails/password_reset.txt"
    extra_context = {
        "title": "Password Reset",
        "subtitle": "Forgot your password?",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps/password_reset.html"
    partial_template_name = "terminusgps/partials/_password_reset.html"
    success_url = reverse_lazy("password reset done")
    subject_template_name = "terminusgps/emails/password_reset_subject.html"

    def get_form(self, form_class: forms.Form | None = None) -> forms.Form:
        form = super().get_form(form_class)
        form.fields["email"].label = "Email Address"
        form.fields["email"].widget.attrs.update(
            {
                "class": "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600",
                "placeholder": "email@domain.com",
            }
        )
        return form


class TerminusgpsPasswordResetDoneView(
    HtmxTemplateResponseMixin, PasswordResetDoneView
):
    content_type = "text/html"
    extra_context = {"title": "Done Password Reset"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_done.html"
    partial_template_name = "terminusgps/partials/_password_reset_done.html"


class TerminusgpsPasswordResetConfirmView(
    HtmxTemplateResponseMixin, PasswordResetConfirmView
):
    content_type = "text/html"
    extra_context = {"title": "Confirm Password Reset", "class": "flex flex-col gap-4"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/password_reset_confirm.html"
    partial_template_name = "terminusgps/partials/_password_reset_confirm.html"
    success_url = reverse_lazy("password reset complete")

    def get_form(self, form_class: forms.Form | None = None) -> forms.Form:
        form = super().get_form(form_class)
        form.fields["new_password1"].label = "New Password"
        form.fields["new_password2"].label = "Confirm New Password"
        for name in form.fields:
            form.fields[name].widget.attrs.update(
                {
                    "class": "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"
                }
            )
        return form


class TerminusgpsPasswordResetCompleteView(
    HtmxTemplateResponseMixin, PasswordResetCompleteView
):
    content_type = "text/html"
    extra_context = {"title": "Completed Password Reset"}
    http_method_names = ["get"]
    template_name = "terminusgps/password_reset_complete.html"
    partial_template_name = "terminusgps/partials/_password_reset_complete.html"


class TerminusgpsLoginView(HtmxTemplateResponseMixin, LoginView):
    authentication_form = TerminusgpsAuthenticationForm
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
        "class": "p-4 flex flex-col gap-2",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("dashboard")
    partial_template_name = "terminusgps/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps/login.html"


class TerminusgpsLogoutView(HtmxTemplateResponseMixin, LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("login")
    partial_template_name = "terminusgps/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps/logout.html"


class TerminusgpsRegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
        "class": "p-4 flex flex-col gap-2",
    }
    form_class = TerminusgpsRegisterForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps/register.html"
    partial_template_name = "terminusgps/partials/_register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(
        self, form: TerminusgpsRegisterForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            ids = self.wialon_registration_flow(form)
            Customer.objects.create(
                user=get_user_model().objects.create_user(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                ),
                wialon_user_id=ids.get("end_user_id"),
                wialon_resource_id=ids.get("resource_id"),
            )
        except WialonError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)

    @staticmethod
    def wialon_registration_flow(
        form: TerminusgpsRegisterForm,
    ) -> dict[str, str | int | None]:
        username: str = form.cleaned_data["username"]
        password: str = form.cleaned_data["password1"]

        with WialonSession() as session:
            super_user = WialonUser(
                id=None,
                session=session,
                creator_id=settings.WIALON_ADMIN_ID,
                name=f"super_{username}",  # super_email@domain.com
                password=password,
            )
            resource = WialonResource(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=f"account_{username}",  # account_email@domain.com
            )
            end_user = WialonUser(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=username,  # email@domain.com
                password=password,
            )

            end_user.grant_access(
                resource, access_mask=constants.ACCESSMASK_RESOURCE_BASIC
            )
            resource.create_account("terminusgps_ext_hist")
            resource.enable_account()
            resource.set_settings_flags()
            resource.add_days(7)

        return {"end_user_id": end_user.id, "resource_id": resource.id}
