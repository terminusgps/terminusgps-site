from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import EmailMultiAlternatives
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, View
from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonResource, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.forms import (
    TrackerAuthenticationForm,
    TrackerEmailVerificationForm,
    TrackerRegisterForm,
)
from terminusgps_tracker.models.customers import Customer
from terminusgps_tracker.views.mixins import HtmxTemplateResponseMixin


class TrackerSendVerificationEmailView(View):
    content_type = "text/html"
    http_method_names = ["get"]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            customer = Customer.objects.get(pk=kwargs["pk"])
            customer.email_otp = customer.generate_email_otp(duration=500)
            customer.save()

            context = self.generate_email_context(request, customer)
            text_content = render_to_string(
                "terminusgps_tracker/emails/verify.txt", context=context
            )
            html_content = render_to_string(
                "terminusgps_tracker/emails/verify.html", context=context
            )
            msg = EmailMultiAlternatives(
                "Terminus GPS - Verify Email",
                text_content,
                "support@terminusgps.com",
                [customer.user.username],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)
            return HttpResponse(status=200)
        except Customer.DoesNotExist:
            return HttpResponse(status=400)

    def generate_email_context(
        self, request: HttpRequest, customer: Customer
    ) -> dict[str, str]:
        return {
            "otp": customer.email_otp,
            "first_name": customer.user.first_name
            or customer.user.username.split("@")[0],
            "link": request.build_absolute_uri(
                reverse("verify email", kwargs={"pk": customer.pk})
            ),
        }


class TrackerVerifyEmailView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Verify Email", "class": "p-4 flex flex-col gap-2"}
    http_method_names = ["get", "post"]
    form_class = TrackerEmailVerificationForm
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_tracker/email_verification.html"
    partial_template_name = "terminusgps_tracker/partials/_email_verification.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        try:
            customer = Customer.objects.get(pk=self.kwargs["pk"])
            context["customer"] = customer
        except Customer.DoesNotExist:
            context["customer"] = None
        return context

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        if self.request.GET.get("otp"):
            initial["otp"] = self.request.GET["otp"]
        return initial

    def form_valid(
        self, form: TrackerEmailVerificationForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            customer = Customer.objects.get(pk=self.kwargs["pk"])
            input_otp = form.cleaned_data["otp"]
            customer_otp = customer.email_otp

            if input_otp == customer_otp:
                customer.email_verified = True
                customer.save()
                return super().form_valid(form=form)
            else:
                form.add_error(
                    "otp",
                    ValidationError(
                        _("Whoops! OTP was invalid, please try again later.")
                    ),
                )
                return self.form_invalid(form=form)

        except Customer.DoesNotExist:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Couldn't find a customer for your account.")
                ),
            )
            return self.form_invalid(form=form)


class TrackerLoginView(HtmxTemplateResponseMixin, LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
        "class": "p-4 flex flex-col gap-2",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("dashboard")
    partial_template_name = "terminusgps_tracker/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_tracker/login.html"


class TrackerLogoutView(HtmxTemplateResponseMixin, LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps_tracker/logout.html"


class TrackerRegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
        "class": "p-4 flex flex-col gap-2",
    }
    form_class = TrackerRegisterForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/register.html"
    partial_template_name = "terminusgps_tracker/partials/_register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(
        self, form: TrackerRegisterForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            ids = self.wialon_registration_flow(form)
            Customer.objects.create(
                user=get_user_model().objects.create_user(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                ),
                wialon_user_id=ids.get("end_user_id"),
                wialon_super_user_id=ids.get("super_user_id"),
                wialon_group_id=ids.get("group_id"),
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
        form: TrackerRegisterForm,
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
            unit_group = WialonUnitGroup(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=f"group_{username}",  # group_email@domain.com
            )

            end_user.grant_access(
                unit_group, access_mask=constants.ACCESSMASK_UNIT_BASIC
            )
            end_user.grant_access(
                resource, access_mask=constants.ACCESSMASK_RESOURCE_BASIC
            )
            resource.create_account("terminusgps_ext_hist")
            resource.enable_account()
            resource.set_settings_flags()
            resource.add_days(7)

        return {
            "end_user_id": end_user.id,
            "group_id": unit_group.id,
            "resource_id": resource.id,
            "super_user_id": super_user.id,
        }
