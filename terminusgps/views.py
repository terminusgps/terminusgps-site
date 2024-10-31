from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wialon import WialonError
from django.utils.translation import gettext_lazy as _

from terminusgps.forms import (
    TerminusLoginForm,
    TerminusRegistrationForm,
    TerminusPasswordResetForm,
)
from terminusgps_tracker.models import CustomerProfile
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items import (
    WialonUnitGroup,
    WialonUser,
    WialonResource,
)


class TerminusPasswordResetView(PasswordResetView):
    form_class = TerminusPasswordResetForm
    content_type = "text/html"
    email_template_name = "terminusgps/emails/password_reset_email.html"
    extra_context = {"title": "Password Reset"}
    extra_email_context = {"subject": "Terminus GPS Password Reset"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/password_reset.html"
    success_url = reverse_lazy("login")


class TerminusAboutView(TemplateView):
    template_name = "terminusgps/about.html"
    content_type = "text/html"
    extra_context = {"title": "About"}
    http_method_names = ["get"]


class TerminusContactView(TemplateView, FormView):
    template_name = "terminusgps/contact.html"
    content_type = "text/html"
    extra_context = {"title": "Contact"}
    http_method_names = ["get", "post"]


class TerminusPrivacyView(TemplateView):
    template_name = "terminusgps/privacy.html"
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]


class TerminusSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = "https://github.com/terminus-gps/terminusgps-site"


class TerminusLoginView(LoginView):
    authentication_form = TerminusLoginForm
    content_type = "text/html"
    extra_context = {"title": "Login"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("profile")
    partial_template_name = "terminusgps/partials/_login.html"
    template_name = "terminusgps/login.html"

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


class TerminusLogoutView(LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_logout.html"
    success_url = reverse_lazy("login")
    template_name = "terminusgps/logout.html"


class TerminusRegistrationHelpView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Help Registration"}
    http_method_names = ["get"]
    template_name = "terminusgps/help_register.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = TerminusRegistrationForm
        return context


class TerminusRegistrationView(FormView):
    form_class = TerminusRegistrationForm
    content_type = "text/html"
    extra_context = {"title": "Register"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/register.html"
    partial_template_name = "terminusgps/partials/_register.html"
    success_url = reverse_lazy("login")

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

    def get_user(self, form: TerminusRegistrationForm) -> AbstractBaseUser:
        user, created = get_user_model().objects.get_or_create(
            username=form.cleaned_data["username"]
        )
        if created:
            user.set_password(form.cleaned_data["password1"])
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()
        return user

    def get_profile(self, user: AbstractBaseUser) -> CustomerProfile:
        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        return profile

    def form_valid(self, form: TerminusRegistrationForm) -> HttpResponse:
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
            wialon_group.grant_access(user=wialon_end_user)
            profile.wialon_super_user_id = wialon_super_user.id
            profile.wialon_user_id = wialon_end_user.id
            profile.wialon_group_id = wialon_group.id
            profile.wialon_resource_id = wialon_resource.id
            profile.save()


class TerminusProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps/profile.html"
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def get_profile(self) -> CustomerProfile | None:
        return CustomerProfile.objects.get(user=self.request.user) or None

    def get_title(self) -> str:
        return f"{self.request.user.username}'s Profile"

    def get_wialon_items(self) -> list:
        profile = self.get_profile()
        try:
            with WialonSession() as session:
                group = WialonUnitGroup(
                    id=str(profile.wialon_group_id), session=session
                )
                return group.items
        except WialonError:
            return [None]

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        context["profile"] = self.get_profile()
        context["wialon_items"] = self.get_wialon_items()
        return context
