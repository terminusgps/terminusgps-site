from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from wialon import WialonError

from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerRegistrationForm
from terminusgps_tracker.models import TrackerProfile
from terminusgps_tracker.models.customer import TodoItem, TodoList
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
    partial_template_name = "terminusgps_tracker/partials/_login.html"
    template_name = "terminusgps_tracker/login.html"

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if not self.request.headers.get("HX-Request"):
            return super().render_to_response(context, **response_kwargs)
        return self.response_class(
            request=self.request,
            template=self.partial_template_name,
            context=context,
            using=self.template_engine,
            **response_kwargs,
        )


class TrackerLogoutView(LogoutView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    extra_context = {"title": "Logout"}
    partial_template_name = "terminusgps_tracker/partials/_logout.html"
    success_url = reverse_lazy("tracker login")
    template_name = "terminusgps_tracker/logout.html"


class TrackerRegistrationView(FormView):
    form_class = TrackerRegistrationForm
    content_type = "text/html"
    extra_context = {
        "title": "Registration",
        "subtitle": "Start tracking your vehicles with the Terminus GPS Tracker",
    }
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/register.html"
    partial_template_name = "terminusgps_tracker/partials/_register.html"
    success_url = reverse_lazy("tracker login")

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        if self.request.headers.get("HX-Request"):
            return self.response_class(
                request=self.request,
                template=self.partial_template_name,
                context=context,
                using=self.template_engine,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)

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

    def get_profile(self, user: AbstractBaseUser) -> TrackerProfile:
        profile, _ = TrackerProfile.objects.get_or_create(user=user)
        return profile

    def form_valid(self, form: TrackerRegistrationForm) -> HttpResponse:
        profile = self.get_profile(user=self.get_user(form=form))
        try:
            self.wialon_registration_flow(form=form, profile=profile)
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
        self, form: TrackerRegistrationForm, profile: TrackerProfile
    ) -> None:
        with WialonSession() as session:
            # Retrieved
            wialon_admin_user = WialonUser(id="27881459", session=session)

            # Created
            wialon_super_user = WialonUser(
                owner=wialon_admin_user,
                name=f"super_{form.cleaned_data["username"]}",
                password=form.cleaned_data["password1"],
                session=session,
            )
            # Created
            wialon_end_user = WialonUser(
                owner=wialon_super_user,
                name=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                session=session,
            )
            # Created
            wialon_group = WialonUnitGroup(
                owner=wialon_super_user,
                name=f"{form.cleaned_data["username"]}'s Group",
                session=session,
            )
            # Created
            wialon_resource = WialonResource(
                owner=wialon_super_user,
                name=f"{form.cleaned_data["username"]} Resource",
                session=session,
            )
            wialon_group.grant_access(user=wialon_end_user)
            profile.wialon_super_user_id = wialon_super_user.id
            profile.wialon_user_id = wialon_end_user.id
            profile.wialon_group_id = wialon_group.id
            profile.wialon_resource_id = wialon_resource.id
            todos = (
                TodoItem.objects.create(
                    label="Register your first asset", view="upload asset"
                ),
                TodoItem.objects.create(
                    label="Upload a payment method", view="upload payment"
                ),
            )
            TodoList.objects.create(profile=profile, items=[todos])
            profile.save()
