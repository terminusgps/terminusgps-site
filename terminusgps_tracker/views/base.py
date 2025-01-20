from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.views.generic import View, TemplateView
from django.views.generic.base import ContextMixin

from terminusgps_tracker.models import TrackerProfile
from terminusgps.wialon.session import WialonSession


class WialonSessionView(View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Initializes a Wialon session for use in the view."""
        if not hasattr(settings, "WIALON_TOKEN"):
            raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")

        session = WialonSession(sid=request.session.get("wialon_sid"))
        if not session.active:
            session.login(token=settings.WIALON_TOKEN)
            request.session["wialon_sid"] = session.id
        self.wialon_sid = request.session["wialon_sid"]
        return super().setup(request, *args, **kwargs)


class HtmxTemplateView(TemplateView):
    partial_template_name: str = ""

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        htmx_request = bool(request.headers.get("HX-Request"))
        boosted = bool(request.headers.get("HX-Boosted"))

        if htmx_request and not boosted:
            self.template_name = self.partial_template_name
        return super().setup(request, *args, **kwargs)


class ProfileContextView(ContextMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if request.user and request.user.is_authenticated:
            self.profile, _ = TrackerProfile.objects.get_or_create(user=request.user)
        else:
            self.profile = None
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context


class TrackerProfileContextView(ContextMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if not hasattr(settings, "TRACKER_PROFILE"):
            raise ImproperlyConfigured("'TRACKER_PROFILE' setting is required.")
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["tracker_profile"] = settings.TRACKER_PROFILE
        return context


class TrackerBaseView(
    HtmxTemplateView, WialonSessionView, ProfileContextView, TrackerProfileContextView
):
    """Terminus GPS Tracker base view. Includes HTMX functionality, a Wialon session, the tracker profile and user profile."""
