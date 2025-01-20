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
        """Initializes and/or refreshes a Wialon session for use in the view."""
        if not hasattr(settings, "WIALON_TOKEN"):
            raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")

        if not request.session.get("wialon_sid"):
            session = WialonSession()
            session.login(token=settings.WIALON_TOKEN)
            request.session["wialon_sid"] = session.id
        self.wialon_sid = request.session["wialon_sid"]

        if not self.wialon_active_session:
            self.wialon_refresh_session()
        return super().setup(request, *args, **kwargs)

    @property
    def wialon_active_session(self) -> bool:
        """
        Whether or not the Wialon session is currently active.

        :type: :py:obj:`bool`

        """
        return WialonSession(sid=self.wialon_sid).active

    def wialon_refresh_session(self) -> None:
        """
        Refreshes the Wialon session while keeping the current session id valid.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        session = WialonSession(sid=self.wialon_sid)
        session.login(token=settings.WIALON_TOKEN)


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
