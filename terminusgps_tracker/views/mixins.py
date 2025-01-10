from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin

from terminusgps_tracker.models import TrackerProfile


class HtmxMixin(TemplateResponseMixin, View):
    partial_template_name: str = ""

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        htmx_request = bool(request.headers.get("HX-Request"))
        boosted = bool(request.headers.get("HX-Boosted"))

        if htmx_request and not boosted:
            self.template_name = self.partial_template_name
        return super().setup(request, *args, **kwargs)


class ProfileRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."

    def test_func(self) -> bool | None:
        test_result = None
        if self.request.user and isinstance(self.request.user, get_user_model()):
            try:
                assert self.request.user.is_authenticated, "User isn't authenticated"
                TrackerProfile.objects.get(pk=self.request.user.pk)
                test_result = True
            except (TrackerProfile.DoesNotExist, AssertionError):
                test_result = False
            finally:
                return test_result


class ProfileContextMixin(ContextMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.profile = TrackerProfile.objects.get(
            user=request.user
            if request.user and request.user.is_authenticated
            else None
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context
