from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.template.loader import render_to_string
from django.forms import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView
from terminusgps.wialon.items import WialonResource, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerSignupForm
from terminusgps_tracker.models import TrackerProfile, TrackerSubscription
from terminusgps_tracker.views.mixins import HtmxMixin, ProfileContextMixin


class TrackerRegistrationView(RedirectView):
    url = reverse_lazy("tracker signup")
    permanent = True


class TrackerLoginView(LoginView, HtmxMixin):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
        "class": "p-4 flex flex-col gap-4",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    partial_template_name = "terminusgps_tracker/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/login.html"


class TrackerLogoutView(LogoutView, ProfileContextMixin, HtmxMixin):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps_tracker/logout.html"


class TrackerSignupView(FormView, SuccessMessageMixin, HtmxMixin):
    content_type = "text/html"
    extra_context = {
        "title": "Sign Up",
        "subtitle": "You'll know where yours are...",
        "class": "p-4 flex flex-col gap-4",
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
            )
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form=form)
        else:
            user = get_user_model().objects.create_user(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["username"],
            )
            self.profile = TrackerProfile.objects.create(user=user)
            TrackerSubscription.objects.create(profile=self.profile)
            self.profile.wialon_super_user_id = ids.get("super_user")
            self.profile.wialon_end_user_id = ids.get("end_user")
            self.profile.wialon_resource_id = ids.get("resource")
            self.profile.wialon_group_id = ids.get("unit_group")
            self.profile.save()
        return super().form_valid(form=form)

    # TODO: retrieve templates from AWS
    @staticmethod
    def send_verification_email(to_addr: str) -> None:
        now = timezone.now()
        text_content: str = render_to_string(
            "terminusgps_tracker/emails/signup_success.txt",
            context={"email": to_addr, "now": now},
        )
        html_content: str = render_to_string(
            "terminusgps/emails/signup_success.html",
            context={"email": to_addr, "now": now},
        )
        email: EmailMultiAlternatives = EmailMultiAlternatives(
            f"Bug Report - {timezone.now():%d/%m/%y} - {timezone.now():%I:%M:%S%z}",
            text_content,
            to=[to_addr],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def wialon_registration_flow(self, username: str, password: str) -> dict:
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            admin_id = settings.WIALON_ADMIN_ID
            super_user = self._wialon_create_user(
                creator_id=admin_id,
                username=f"account_{username}",
                password=password,
                session=session,
            )
            resource = self._wialon_create_resource(
                creator_id=super_user.id, name=f"account_{username}", session=session
            )
            end_user = self._wialon_create_user(
                creator_id=admin_id,
                username=username,
                password=password,
                session=session,
            )
            unit_group = self._wialon_create_group(
                creator_id=admin_id, name=f"group_{username}", session=session
            )
            self._wialon_create_account(resource_id=resource.id, session=session)

            return {
                "end_user": end_user.id,
                "super_user": super_user.id,
                "unit_group": unit_group.id,
                "resource": resource.id,
            }

    @staticmethod
    def _wialon_create_account(
        resource_id: int | None,
        session: WialonSession,
        plan: str = "terminusgps_ext_hist",
    ) -> None:
        try:
            if resource_id is None:
                raise ValueError

            session.wialon_api.account_create_account(
                **{"itemId": str(resource_id), "plan": plan}
            )
            session.wialon_api.account_enable_account(
                **{"itemId": str(resource_id), "enable": str(int(False))}
            )
        except (WialonError, ValueError) as e:
            print(e)
            raise ValidationError(
                _("Whoops! Failed to create Wialon account: #'%(value)s'"),
                code="wialon",
                params={"value": resource_id},
            )

    @staticmethod
    def _wialon_create_resource(
        creator_id: int | None, name: str, session: WialonSession
    ) -> WialonResource:
        try:
            if creator_id is None:
                raise ValueError

            resource = WialonResource(creator_id=creator_id, name=name, session=session)
            return resource
        except (WialonError, ValueError) as e:
            print(e)
            raise ValidationError(
                _("Whoops! Failed to create Wialon resource: '%(value)s'"),
                code="wialon",
                params={"value": name},
            )

    @staticmethod
    def _wialon_create_group(
        creator_id: int, name: str, session: WialonSession
    ) -> WialonUnitGroup:
        try:
            group = WialonUnitGroup(creator_id=creator_id, name=name, session=session)
            return group
        except (WialonError, ValueError):
            raise ValidationError(
                _("Whoops! Failed to create Wialon group: '%(value)s'"),
                code="wialon",
                params={"value": name},
            )

    @staticmethod
    def _wialon_create_user(
        creator_id: int, username: str, password: str, session: WialonSession
    ) -> WialonUser:
        try:
            user = WialonUser(
                creator_id=creator_id, name=username, password=password, session=session
            )
            return user
        except (WialonError, ValueError):
            raise ValidationError(
                _("Whoops! Failed to create Wialon user: '%(value)s'"),
                code="wialon",
                params={"value": username},
            )

    @staticmethod
    def _wialon_get_user(user_id: int, session: WialonSession) -> WialonUser:
        try:
            user = WialonUser(id=str(user_id), session=session)
            return user
        except (WialonError, ValueError):
            raise ValidationError(
                _("Whoops! Failed to retrieve Wialon user: #'%(value)s'"),
                code="wialon",
                params={"value": user_id},
            )
