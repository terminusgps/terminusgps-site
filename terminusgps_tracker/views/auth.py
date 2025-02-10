from typing import Any

from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.translation import gettext_lazy as _
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView
from wialon.api import WialonError

from terminusgps.wialon.items import WialonResource, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerSignupForm
from terminusgps_tracker.models import TrackerProfile, TrackerSubscription
from terminusgps_tracker.views.base import (
    HtmxTemplateView,
    TrackerBaseView,
    WialonSessionView,
)


def send_confirmation_email(email: str) -> None:
    subject = "Signed up! - Terminus GPS"
    html_content = render_to_string(
        "terminusgps_tracker/emails/signup_success.html",
        {"email": email, "now": timezone.now()},
    )
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(
        subject, text_content, "support@terminusgps.com", [email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=True)


class TrackerRegistrationView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    query_string = True
    url = reverse_lazy("asset create")


class TrackerLoginView(LoginView, HtmxTemplateView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
        "class": "p-4 flex flex-col gap-2",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    partial_template_name = "terminusgps_tracker/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/login.html"


class TrackerLogoutView(LogoutView, TrackerBaseView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps_tracker/logout.html"


class TrackerSignupView(
    FormView, SuccessMessageMixin, HtmxTemplateView, WialonSessionView
):
    content_type = "text/html"
    extra_context = {
        "title": "Sign Up",
        "subtitle": "You'll know where yours are...",
        "class": "p-4 flex flex-col gap-2",
    }
    form_class = TrackerSignupForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_signup.html"
    success_message = "%(username)s's account was created succesfully"
    success_url = reverse_lazy("tracker login")
    template_name = "terminusgps_tracker/signup.html"

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def form_valid(self, form: TrackerSignupForm) -> HttpResponse:
        try:
            ids = self.wialon_registration_flow(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                session=self.wialon_session,
            )
        except (ValueError, WialonError) as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! Something went wrong with Wialon: '%(error)s'."),
                    code="wialon",
                    params={"error": e},
                ),
            )
            return self.form_invalid(form=form)

        profile = TrackerProfile.objects.create(
            user=get_user_model().objects.create_user(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["username"],
            )
        )
        TrackerSubscription.objects.create(profile=profile)
        profile.wialon_super_user_id = ids.get("super_user")
        profile.wialon_end_user_id = ids.get("end_user")
        profile.wialon_resource_id = ids.get("resource")
        profile.wialon_group_id = ids.get("unit_group")
        profile.save()
        send_confirmation_email(form.cleaned_data["username"])
        return super().form_valid(form=form)

    @staticmethod
    @transaction.atomic
    def wialon_registration_flow(
        username: str, password: str, session: WialonSession
    ) -> dict[str, int | None]:
        super_user = WialonUser(
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"account_{username}",  # account_email@domain.com
            password=password,
            session=session,
        )
        end_user = WialonUser(
            creator_id=settings.WIALON_ADMIN_ID,
            name=username,  # email@domain.com
            password=password,
            session=session,
        )
        unit_group = WialonUnitGroup(
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"group_{username}",  # group_email@domain.com
            session=session,
        )
        resource = WialonResource(
            creator_id=super_user.id, name=f"account_{username}", session=session
        )
        session.wialon_api.account_create_account(
            **{"itemId": resource.id, "plan": "terminusgps_ext_hist"}
        )
        session.wialon_api.account_enable_account(
            **{"itemId": resource.id, "enable": int(True)}
        )

        return {
            "super_user": super_user.id,
            "end_user": end_user.id,
            "resource": resource.id,
            "unit_group": unit_group.id,
        }
