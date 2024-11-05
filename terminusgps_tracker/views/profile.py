from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from terminusgps_tracker.models.customer import TrackerProfile


class TrackerSubscriptionView(TemplateView):
    template_name = "terminusgps_tracker/subscriptions.html"
    content_type = "text/html"
    extra_context = {"title": "Subscriptions", "subtitle": "Our subscription options"}
    http_method_names = ["get"]


class TrackerAboutView(TemplateView):
    template_name = "terminusgps_tracker/about.html"
    content_type = "text/html"
    extra_context = {"title": "About", "subtitle": "Why are we even doing this?"}
    http_method_names = ["get"]


class TrackerContactView(TemplateView):
    template_name = "terminusgps_tracker/contact.html"
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Get in touch with us"}
    http_method_names = ["get", "post"]


class TrackerPrivacyView(TemplateView):
    template_name = "terminusgps_tracker/privacy.html"
    content_type = "text/html"
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_SOURCE_URL


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile.html"
    extra_context = {"subtitle": settings.TRACKER_MOTD}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if (
            not request.user.is_authenticated
            or not TrackerProfile.objects.filter(user=request.user).exists()
        ):
            self.profile = None
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = f"{self.profile.user.first_name}'s Profile"
        context["profile"] = self.profile
        return context
