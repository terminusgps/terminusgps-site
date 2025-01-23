from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView


from terminusgps_tracker.forms import (
    BugReportForm,
    EmailNewsletterForm,
    EmailInquiryForm,
)
from terminusgps_tracker.views.base import TrackerBaseView


class TrackerLandingView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = reverse_lazy("tracker about")


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_PROFILE["GITHUB"]


class TrackerAboutView(TrackerBaseView):
    extra_context = {"title": "About", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/about.html"
    partial_template_name = "terminusgps_tracker/partials/_about.html"


class TrackerPrivacyView(TrackerBaseView):
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/privacy.html"
    partial_template_name = "terminusgps_tracker/partials/_privacy.html"


class TrackerContactView(TrackerBaseView):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Ready to get in touch?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/contact.html"
    partial_template_name = "terminusgps_tracker/partials/_contact.html"


class TrackerNewsletterSignupView(FormView, TrackerBaseView):
    content_type = "text/html"
    extra_context = {"title": "Newsletter"}
    form_class = EmailNewsletterForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_newsletter_signup.html"
    template_name = "terminusgps_tracker/newsletter_signup.html"

    def form_valid(self, form: EmailNewsletterForm) -> HttpResponse:
        return super().form_valid(form=form)


class TrackerEmailInquiryView(FormView, TrackerBaseView, SuccessMessageMixin):
    content_type = "text/html"
    extra_context = {"class": "flex flex-col gap-2 p-2 bg-gray-300 rounded"}
    form_class = EmailInquiryForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_email_inquiry.html"
    success_message = "Thanks! We'll reach out to '%(email)s' as soon as possible."
    success_url = reverse_lazy("tracker contact")
    template_name = "terminusgps_tracker/email_inquiry.html"

    def form_valid(self, form: EmailInquiryForm) -> HttpResponse:
        return super().form_valid(form=form)

    def get_success_message(self, cleaned_data: dict[str, str]) -> str:
        return self.success_message % {"email": cleaned_data["email"]}


class TrackerBugReportView(FormView, TrackerBaseView, LoginRequiredMixin):
    content_type = "text/html"
    extra_context = {
        "title": "Bug Report",
        "subtitle": "Found a bug?",
        "class": "flex flex-col gap-2 p-4 bg-gray-300 rounded caret-terminus-red-600",
    }
    form_class = BugReportForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_bug_report.html"
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/bug_report.html"
    login_url = reverse_lazy("login")
    raise_exception = False
    permission_denied_message = "Please login and try again."

    def get_initial(self) -> dict[str, Any]:
        return {"user": self.request.user}
