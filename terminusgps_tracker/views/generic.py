from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, RedirectView, FormView
from terminusgps.wialon.items import WialonResource, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError


from terminusgps_tracker.forms import (
    TrackerSignupForm,
    TrackerAuthenticationForm,
    BugReportForm,
)
from terminusgps_tracker.models import TrackerProfile, TrackerSubscription


class TrackerLandingView(LoginRequiredMixin, RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = reverse_lazy("tracker profile")


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_PROFILE["GITHUB"]


class TrackerAboutView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/about.html"


class TrackerPrivacyView(TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy", "profile": settings.TRACKER_PROFILE}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/privacy.html"


class TrackerContactView(TemplateView):
    content_type = "text/html"
    extra_context = {
        "title": "Contact",
        "subtitle": "Ready to get in touch?",
        "profile": settings.TRACKER_PROFILE,
    }
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/contact.html"


class TrackerLoginView(LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {"title": "Login", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/forms/login.html"


class TrackerLogoutView(SuccessMessageMixin, LogoutView):
    content_type = "text/html"
    template_name = "terminusgps_tracker/forms/logout.html"
    extra_context = {"title": "Logout"}
    success_url = reverse_lazy("tracker login")
    success_message = "You have been successfully logged out."
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    http_method_names = ["get", "post", "options"]

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        super().post(request, *args, **kwargs)
        return HttpResponseRedirect(self.success_url)


class TrackerSignupView(SuccessMessageMixin, FormView):
    form_class = TrackerSignupForm
    content_type = "text/html"
    extra_context = {"title": "Sign Up", "subtitle": "You'll know where yours are..."}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/signup.html"
    success_url = reverse_lazy("tracker login")
    success_message = "%(username)s's account was created succesfully"

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def form_valid(self, form: TrackerSignupForm) -> HttpResponse:
        user = get_user_model().objects.create_user(
            first_name=form.cleaned_data["first_name"],
            last_name=form.cleaned_data["last_name"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            email=form.cleaned_data["username"],
        )
        profile = TrackerProfile.objects.create(user=user)
        TrackerSubscription.objects.create(profile=profile)
        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                self.create_wialon_objects(profile, session)
        except WialonError or ValueError:
            print(f"{timezone.now()} - Failed to create Wialon objects.")
        return super().form_valid(form=form)

    @staticmethod
    @transaction.atomic
    def create_wialon_objects(profile: TrackerProfile, session: WialonSession) -> None:
        admin = WialonUser(id=str(settings.WIALON_ADMIN_ID), session=session)
        owner = WialonUser(
            owner_id=admin.id,
            name=f"super_{profile.user.username}",
            password=profile.user.password,
            session=session,
        )
        end_user = WialonUser(
            owner_id=owner.id,
            name=profile.user.username,
            password=profile.user.password,
            session=session,
        )
        group = WialonUnitGroup(
            owner_id=owner.id, name=f"group_{profile.user.username}", session=session
        )
        # resource = WialonResource(
        #     owner_id=owner.id, name=f"resource_{profile.user.username}", session=session
        # )

        profile.wialon_super_user_id = owner.id
        profile.wialon_end_user_id = end_user.id
        profile.wialon_group_id = group.id
        # profile.wialon_resource_id = resource.id
        profile.save()


class TrackerBugReportView(SuccessMessageMixin, FormView):
    form_class = BugReportForm
    content_type = "text/html"
    extra_context = {"title": "Bug Report"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/bug_report.html"
    success_url = reverse_lazy("tracker profile")
    success_message = "Thank you! Your bug report was submitted successfully."

    def form_valid(self, form: BugReportForm) -> HttpResponse:
        self.send_bug_report(form)
        return super().form_valid(form=form)

    def get_initial(self) -> dict[str, Any]:
        if self.request.user:
            return {"user": self.request.user}
        return {}

    @staticmethod
    def send_bug_report(form: BugReportForm) -> None:
        text_content: str = render_to_string(
            "terminusgps_tracker/emails/bug_report.txt",
            context={
                "user": form.cleaned_data["user"],
                "text": form.cleaned_data["text"],
                "category": form.cleaned_data["category"],
                "now": timezone.now(),
            },
        )
        # html_content: str = render_to_string(
        #     "terminusgps/emails/bug_report.html",
        #     context={
        #         "user": form.cleaned_data["user"],
        #         "text": form.cleaned_data["text"],
        #         "category": form.cleaned_data["category"],
        #         "now": timezone.now(),
        #     },
        # )
        email: EmailMultiAlternatives = EmailMultiAlternatives(
            f"Bug Report - {timezone.now():%d/%m/%y} - {timezone.now():%I:%M:%S%z}",
            text_content,
            to=["support@terminusgps.com"],
        )
        # email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=True)
