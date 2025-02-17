from typing import Any


from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.views.generic import View, TemplateView
from django.views.generic.base import ContextMixin
from wialon.api import WialonError

from terminusgps_tracker.models import TrackerProfile
from terminusgps.wialon.session import WialonSession

from .mixins import TrackerAppConfigContextMixin

if not hasattr(settings, "WIALON_TOKEN"):
    raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")
if not hasattr(settings, "WIALON_SESSION_LOGLEVEL"):
    raise ImproperlyConfigured("'WIALON_SESSION_LOGLEVEL' setting is required.")


class WialonSessionView(ContextMixin, View):
    """
    Creates or continues a Wialon API session.

    Adds :py:attr:`wialon_sid` to the view context for use in the front-end.

    """

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        log_level = settings.WIALON_SESSION_LOGLEVEL
        wialon_sid = request.session.get("wialon_sid")

        try:
            self.wialon_session = WialonSession(sid=wialon_sid, log_level=log_level)
            self.wialon_session.wialon_api.avl_evts()
        except WialonError:
            self.wialon_session.login(settings.WIALON_TOKEN)
        finally:
            request.session["wialon_sid"] = self.wialon_session.id
            self.wialon_sid = self.wialon_session.id
            return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["wialon_sid"] = self.wialon_sid
        return context


class HtmxTemplateView(TemplateView):
    """Renders a partial HTML template depending on HTTP headers."""

    content_type = "text/html"
    partial_template_name: str | None = None
    """
    A partial template rendered by htmx.

    :type: :py:obj:`str` | :py:obj:`None`
    :value: :py:obj:`None`
    """

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        htmx_request = bool(request.headers.get("HX-Request"))
        boosted = bool(request.headers.get("HX-Boosted"))

        if htmx_request and self.partial_template_name and not boosted:
            self.template_name = self.partial_template_name
        return super().setup(request, *args, **kwargs)


class ProfileContextView(ContextMixin, View):
    """Adds a user profile into the view context."""

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


class TrackerBaseView(
    HtmxTemplateView,
    WialonSessionView,
    ProfileContextView,
    TrackerAppConfigContextMixin,
):
    """Terminus GPS Tracker base view. Includes HTMX functionality, a Wialon session, the tracker profile and user profile."""
