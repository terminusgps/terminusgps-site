from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView

from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerRegistrationForm
from terminusgps_tracker.models import TrackerProfile
from terminusgps_tracker.integrations.wialon import constants
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.items import (
    WialonUser,
    WialonUnitGroup,
    WialonResource,
)
from terminusgps_tracker.models.customer import TodoItem, TodoList


class TrackerLoginView(LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {"title": "Login"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/forms/login.html"


class TrackerLogoutView(LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("tracker login")
    template_name = "terminusgps_tracker/forms/logout.html"


class TrackerRegistrationView(SuccessMessageMixin, FormView):
    form_class = TrackerRegistrationForm
    content_type = "text/html"
    extra_context = {
        "title": "Registration",
        "subtitle": "Start tracking your vehicles with the Terminus GPS Tracker",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/register.html"
    success_url = reverse_lazy("tracker login")
    success_message = "%(username)s's profile was created succesfully"

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def form_valid(self, form: TrackerRegistrationForm) -> HttpResponse:
        user = get_user_model().objects.create_user(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        profile = self.wialon_registration_flow(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            profile=TrackerProfile.objects.create(user=user),
        )
        profile.todo_list = TodoList.objects.create()
        profile.todo_list.items.set(
            [
                TodoItem.objects.create(
                    label="Register your first asset", view="profile create asset"
                ),
                TodoItem.objects.create(
                    label="Upload a payment method", view="profile create payment"
                ),
                TodoItem.objects.create(
                    label="Select a subscription plan",
                    view="profile create subscription",
                ),
            ]
        )
        profile.save()
        return super().form_valid(form=form)

    def wialon_registration_flow(
        self, username: str, password: str, profile: TrackerProfile
    ) -> TrackerProfile:
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
            return profile
