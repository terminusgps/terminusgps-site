import datetime
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from django.views.generic import RedirectView, TemplateView

from terminusgps_tracker.views.mixins import HtmxTemplateResponseMixin

if not hasattr(settings, "TRACKER_APP_CONFIG"):
    raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")


class TrackerSourceCodeView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG.get("REPOSITORY_URL")


class TrackerPrivacyPolicyView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_privacy.html"
    template_name = "terminusgps_tracker/privacy.html"
    extra_context = {"title": "Privacy Policy", "class": "flex flex-col gap-4"}


class TrackerGreetingView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Greeting", "class": "flex flex-col gap-4"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_greeting.html"
    template_name = "terminusgps_tracker/greeting.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.request.user:
            context["now"] = timezone.now()
            context["name"] = self.request.user.first_name
            context["message"] = self.get_user_greeting(context["now"])
        return context

    def get_user_greeting(self, time: datetime.datetime) -> str | None:
        greetings_map = {
            frozenset({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}): "Good morning",
            frozenset({12, 13, 14, 15, 16}): "Good afternoon",
            frozenset({17, 18, 19, 20, 21, 22, 23, 24}): "Good afternoon",
        }
        for key, value in greetings_map.items():
            if time.astimezone().hour in key:
                return value
        return
