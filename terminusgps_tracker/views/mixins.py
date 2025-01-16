from typing import Any, Callable

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from terminusgps_tracker.models import TrackerProfile
from terminusgps.wialon.session import WialonSession


class WialonSessionMixin(View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if not hasattr(settings, "WIALON_TOKEN"):
            raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")

        if not request.session.get("wialon_sid"):
            session = WialonSession()
            session.login(token=settings.WIALON_TOKEN)
            request.session["wialon_sid"] = session.id
        self.wialon_sid = request.session["wialon_sid"]
        return super().setup(request, *args, **kwargs)


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Sorry, you are not allowed to access this."

    def get_test_func(self) -> Callable:
        def user_is_staff() -> bool:
            if self.request.user and hasattr(self.request.user, "is_staff"):
                return self.request.user.is_staff
            return False

        return user_is_staff


class HtmxMixin(TemplateResponseMixin, View):
    partial_template_name: str = ""

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        htmx_request = bool(request.headers.get("HX-Request"))
        boosted = bool(request.headers.get("HX-Boosted"))

        if htmx_request and not boosted:
            self.template_name = self.partial_template_name
        return super().setup(request, *args, **kwargs)


class ProfileContextMixin(ContextMixin, View):
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
