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
from terminusgps.wialon import constants
from wialon.api import WialonError

from terminusgps.wialon.items import WialonResource, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerSignupForm
from terminusgps_tracker.models import TrackerProfile
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

    @transaction.atomic
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
        else:
            user = get_user_model().objects.create_user(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["username"],
            )

            profile = TrackerProfile.objects.create(user=user)
            profile.wialon_end_user_id = ids.get("wialon_end_user_id")
            profile.wialon_group_id = ids.get("wialon_group_id")
            profile.wialon_resource_id = ids.get("wialon_resource_id")
            profile.wialon_super_user_id = ids.get("wialon_super_user_id")
            return super().form_valid(form=form)

    @staticmethod
    @transaction.atomic
    def wialon_registration_flow(
        username: str, password: str, session: WialonSession
    ) -> dict[str, int | None]:
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

        end_user.grant_access(unit_group, access_mask=constants.ACCESSMASK_UNIT_BASIC)
        end_user.grant_access(resource, access_mask=constants.ACCESSMASK_RESOURCE_BASIC)
        resource.create_account("terminusgps_ext_hist")
        resource.enable_account()
        resource.set_settings_flags()
        resource.add_days(7)

        return {
            "wialon_end_user_id": end_user.id,
            "wialon_group_id": unit_group.id,
            "wialon_resource_id": resource.id,
            "wialon_super_user_id": super_user.id,
        }
