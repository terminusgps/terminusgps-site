import datetime

from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError
from terminusgps_payments.models import CustomerProfile

from terminusgps_manager.models import TerminusGPSCustomer

from .forms import TerminusgpsAuthenticationForm, TerminusgpsRegistrationForm
from .services import wialon_registration_flow
from .tasks import send_email


class PermanentRedirectView(RedirectView):
    """Permanent redirect view."""

    http_method_names = ["get"]
    permanent = True


class HtmxTemplateView(HtmxTemplateResponseMixin, TemplateView):
    """Renders a template partial instead of the full template on htmx request."""

    content_type = "text/html"
    http_method_names = ["get"]


class LogoutTemplateView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get"]
    template_name = "terminusgps/logout.html"


class LogoutView(HtmxTemplateResponseMixin, LogoutViewBase):
    content_type = "text/html"
    extra_context = {"title": "Logged Out"}
    template_name = "terminusgps/logged_out.html"


class LoginView(HtmxTemplateResponseMixin, LoginViewBase):
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
    }
    form_class = TerminusgpsAuthenticationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps/login.html"


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
            user.save()

            customer_profile = CustomerProfile(user=user)
            customer_profile.email = user.email
            customer_profile.merchant_id = (
                f"{user.first_name} {user.last_name}"
            )
            customer_profile.save()

            customer = TerminusGPSCustomer()
            customer.user = user
            customer.save()
            wialon_registration_flow(form, customer)
            send_email.enqueue(
                to=[user.email],
                subject="Terminus GPS - Account Created",
                template_name="terminusgps/emails/account_created.txt",
                html_template_name="terminusgps/emails/account_created.html",
                context={
                    "fn": user.first_name,
                    "date": datetime.date.today().strftime("%Y-%m-%d"),
                    "platform_link": "https://hosting.terminusgps.com",
                    "support_link": "mailto:support@terminusgps.com",
                    "contact_link": "https://app.terminusgps.com/contact/",
                    "subscribing_link": "https://app.terminusgps.com/subscriptions/",
                },
            )
            return super().form_valid(form=form)
        except (AuthorizenetControllerExecutionError, WialonAPIError) as error:
            form.add_error(None, ValidationError(str(error), code="invalid"))
            return self.form_invalid(form=form)
