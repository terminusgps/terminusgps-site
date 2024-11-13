from typing import Any

from django.views.generic import TemplateView, RedirectView
from django.conf import settings

from terminusgps_tracker.http import HttpRequest
from terminusgps_tracker.models import TrackerProfile


class TrackerSubscriptionView(TemplateView):
    template_name = "terminusgps_tracker/subscriptions.html"
    content_type = "text/html"
    extra_context = {"title": "Subscriptions"}
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.user and request.user.is_authenticated:
            try:
                self.profile = TrackerProfile.objects.get(user=request.user)
            except TrackerProfile.DoesNotExist:
                self.profile = None
        else:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context


class TrackerAboutView(TemplateView):
    template_name = "terminusgps_tracker/about.html"
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get"]


class TrackerContactView(TemplateView):
    template_name = "terminusgps_tracker/contact.html"
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get"]


class TrackerPrivacyView(TemplateView):
    template_name = "terminusgps_tracker/privacy.html"
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_PROFILE["GITHUB"]
