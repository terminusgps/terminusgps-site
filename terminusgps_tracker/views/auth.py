from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import FormView
from terminusgps.wialon.items import WialonUser, WialonUnitGroup, WialonResource
from terminusgps.wialon.items.account import WialonAccount
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerSignupForm
from terminusgps_tracker.models import TrackerProfile, TrackerSubscription


class TrackerLoginView(LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {"title": "Login", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/login.html"


class TrackerLogoutView(LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("tracker login")
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps_tracker/logged_out.html"
    partial_name = "terminusgps_tracker/logout.html"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)


class TrackerSignupView(SuccessMessageMixin, FormView):
    form_class = TrackerSignupForm
    content_type = "text/html"
    extra_context = {"title": "Sign Up", "subtitle": "You'll know where yours are..."}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/signup.html"
    partial_template_name = "terminusgps_tracker/partials/_signup.html"
    success_url = reverse_lazy("tracker login")
    success_message = "%(username)s's account was created succesfully"

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def form_valid(self, form: TrackerSignupForm) -> HttpResponse:
        try:
            ids = self.create_wialon_account(
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
            self.profile.wialon_end_user_id = ids.get("end_user")
            self.profile.wialon_super_user_id = ids.get("super_user")
            self.profile.wialon_resource_id = ids.get("resource")
            self.profile.wialon_group_id = ids.get("unit_group")
            self.profile.save()
        return super().form_valid(form=form)

    @transaction.atomic
    def create_wialon_account(
        self, username: str, password: str
    ) -> dict[str, int | None]:
        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                admin_user = WialonUser(
                    id=str(settings.WIALON_ADMIN_ID), session=session
                )
                super_user = WialonUser(
                    creator_id=admin_user.id,
                    name=f"super_{username}",
                    password=password,
                    session=session,
                )
                unit_group = WialonUnitGroup(
                    creator_id=super_user.id, name=f"group_{username}", session=session
                )
                end_user = WialonUser(
                    creator_id=super_user.id,
                    name=username,
                    password=password,
                    session=session,
                )
                resource = WialonResource(
                    creator_id=end_user.id, name=username, session=session
                )
                return {
                    "end_user": end_user.id,
                    "super_user": super_user.id,
                    "resource": resource.id,
                    "unit_group": unit_group.id,
                }
        except WialonError:
            raise ValidationError(
                _("Whoops! Something went wrong with Wialon. Please try again later.")
            )
        except AssertionError:
            raise ValidationError(
                _("Whoops! Something went wrong on our end. Please try again later.")
            )
