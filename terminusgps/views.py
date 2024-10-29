from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wialon import WialonError
from django.utils.translation import gettext_lazy as _

from terminusgps.forms import TerminusRegistrationForm
from terminusgps_tracker.models import CustomerProfile
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items import (
    WialonUnitGroup,
    WialonUser,
    WialonResource,
)


class TerminusLoginView(LoginView):
    content_type = "text/html"
    extra_context = {"title": "Login"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("profile")
    template_name = "terminusgps/login.html"


class TerminusLogoutView(LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/logout.html"
    success_url = reverse_lazy("login")


class TerminusRegistrationHelpView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Help Registration"}
    http_method_names = ["get"]
    template_name = "terminusgps/help_register.html"


class TerminusRegistrationView(FormView):
    form_class = TerminusRegistrationForm
    content_type = "text/html"
    extra_context = {"title": "Register"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form: TerminusRegistrationForm) -> HttpResponse:
        user = get_user_model().objects.create_user(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        profile = CustomerProfile.objects.create(user=user)
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
        self, form: TerminusRegistrationForm, profile: CustomerProfile
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
            profile.wialon_super_user_id = wialon_super_user.id
            profile.wialon_user_id = wialon_end_user.id
            profile.wialon_group_id = wialon_group.id
            profile.wialon_resource_id = wialon_resource.id
            profile.save()


class TerminusProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps/profile.html"
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login and try again."
    raise_exception = True

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = f"{self.request.user.first_name}'s Profile"
        return context
