from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from wialon import WialonError

from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerRegistrationForm
from terminusgps_tracker.http import HttpRequest
from terminusgps_tracker.models import TrackerProfile
from terminusgps_tracker.models.customer import TodoItem, TodoList
from terminusgps_tracker.integrations.wialon import constants
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.items import (
    WialonUser,
    WialonUnitGroup,
    WialonResource,
)


class TrackerLoginView(LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {"title": "Login"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/login.html"


class TrackerLogoutView(LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker login")
    template_name = "terminusgps_tracker/logout.html"


class TrackerRegistrationView(SuccessMessageMixin, FormView):
    form_class = TrackerRegistrationForm
    content_type = "text/html"
    extra_context = {
        "title": "Registration",
        "subtitle": "Start tracking your vehicles with the Terminus GPS Tracker",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/register.html"
    success_url = reverse_lazy("tracker login")
    success_message = "%(username)s's profile was created succesfully"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.user = request.user or None

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def get_user(self, form: TrackerRegistrationForm) -> AbstractBaseUser:
        user, created = get_user_model().objects.get_or_create(
            username=form.cleaned_data["username"]
        )
        if created:
            user.set_password(form.cleaned_data["password1"])
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()
        return user

    def form_valid(self, form: TrackerRegistrationForm) -> HttpResponse:
        user = self.get_user(form)
        profile, created = TrackerProfile.objects.get_or_create(user=user)
        try:
            self.wialon_registration_flow(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                profile=profile,
            )
        except WialonError:
            form.add_error(
                "username",
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end. Please try again later."
                    )
                ),
            )
        return super().form_valid(form=form)

    def wialon_registration_flow(
        self, username: str, password: str, profile: TrackerProfile
    ) -> None:
        with WialonSession() as session:
            # Retrieved
            wialon_admin_user = WialonUser(id="27881459", session=session)

            # Created
            wialon_super_user = WialonUser(
                owner=wialon_admin_user,
                name=f"super_{username}",
                password=password,
                session=session,
            )
            # Created
            wialon_end_user = WialonUser(
                owner=wialon_super_user,
                name=username,
                password=password,
                session=session,
            )
            # Created
            wialon_group = WialonUnitGroup(
                owner=wialon_super_user, name=f"group_{username}", session=session
            )
            # Created
            wialon_resource = WialonResource(
                owner=wialon_super_user, name=f"resource_{username}", session=session
            )

            wialon_group.grant_access(
                user=wialon_super_user, access_mask=constants.UNIT_FULL_ACCESS_MASK
            )
            wialon_group.grant_access(
                user=wialon_end_user, access_mask=constants.UNIT_BASIC_ACCESS_MASK
            )

            profile.wialon_super_user_id = wialon_super_user.id
            profile.wialon_user_id = wialon_end_user.id
            profile.wialon_group_id = wialon_group.id
            profile.wialon_resource_id = wialon_resource.id
            profile.save()
