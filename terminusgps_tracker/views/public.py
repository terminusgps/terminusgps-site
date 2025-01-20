from typing import Any

from django import forms
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
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


class TrackerBugReportView(TrackerBaseView):
    content_type = "text/html"
    extra_context = {
        "title": "Bug Report",
        "subtitle": "Found a bug?",
        "class": "flex flex-col gap-2 p-2 bg-gray-300 rounded",
    }
    form_class = BugReportForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_bug_report.html"
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/bug_report.html"

    def get_form(self, form_class=None) -> forms.Form:
        form = super().get_form(form_class)
        form.fields["category"].widget.attrs.update(
            {"class": "p-2 bg-gray-200 rounded"}
        )
        return form

    def form_valid(self, form: BugReportForm) -> HttpResponse:
        self.send_bug_report(form)
        return super().form_valid(form=form)

    def get_initial(self) -> dict[str, Any]:
        return {"user": self.request.user or None}

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
        email.send()
