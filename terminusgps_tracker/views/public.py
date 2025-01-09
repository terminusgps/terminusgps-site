from typing import Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, RedirectView, FormView


from terminusgps_tracker.forms import BugReportForm
from terminusgps_tracker.views.mixins import (
    HtmxMixin,
    ProfileContextMixin,
    ProfileRequiredMixin,
)


class TrackerLandingView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = reverse_lazy("tracker about")


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_PROFILE["GITHUB"]


class TrackerAboutView(TemplateView, ProfileContextMixin, HtmxMixin):
    extra_context = {"title": "About", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/about.html"
    partial_template_name = "terminusgps_tracker/partials/_about.html"


class TrackerPrivacyView(TemplateView, ProfileContextMixin, HtmxMixin):
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/privacy.html"
    partial_template_name = "terminusgps_tracker/partials/_privacy.html"


class TrackerContactView(TemplateView, ProfileContextMixin, HtmxMixin):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Ready to get in touch?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/contact.html"
    partial_template_name = "terminusgps_tracker/partials/_contact.html"


class TrackerBugReportView(
    FormView, ProfileRequiredMixin, ProfileContextMixin, HtmxMixin
):
    content_type = "text/html"
    extra_context = {"title": "Bug Report", "subtitle": "Found a bug?"}
    form_class = BugReportForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    success_message = "Thank you! Your bug report was submitted successfully."
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/bug_report.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)

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
