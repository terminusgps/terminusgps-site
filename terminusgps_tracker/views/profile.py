from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from terminusgps_tracker.models.customer import TrackerProfile
from terminusgps_tracker.wialonapi.items import WialonUnitGroup
from terminusgps_tracker.wialonapi.session import WialonSession


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
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def get_profile(self) -> TrackerProfile | None:
        return TrackerProfile.objects.get(user=self.request.user) or None

    def get_title(self) -> str:
        return f"{self.request.user.username}'s Profile"

    def get_wialon_items(self) -> list[str]:
        profile = self.get_profile()
        wialon_items: list[str] = []
        if profile and profile.wialon_group_id:
            with WialonSession() as session:
                group = WialonUnitGroup(
                    id=str(profile.wialon_group_id), session=session
                )
                wialon_items.extend(group.items)
        return wialon_items

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        wialon_items = self.get_wialon_items()

        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["title"] = self.get_title()
        context["profile"] = self.get_profile()
        context["wialon_items"] = wialon_items
        context["num_wialon_items"] = len(wialon_items)
        return context
