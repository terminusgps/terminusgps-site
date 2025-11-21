import logging

from django.conf import settings
from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession

from ..forms import TerminusgpsAuthenticationForm, TerminusgpsRegistrationForm
from ..utils import wialon_account_registration_flow

logger = logging.getLogger(__name__)


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
        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                user = form.save(commit=True)
                user.email = form.cleaned_data["username"]
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.save(update_fields=["email", "first_name", "last_name"])
                wialon_account_registration_flow(user, form, session)
                return super().form_valid(form=form)
        except (ValueError, WialonAPIError) as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(e)s"), code="invalid", params={"e": str(e)}
                ),
            )
            return self.form_invalid(form=form)
