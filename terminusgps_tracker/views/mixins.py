from typing import Any

from django.http import HttpRequest
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


class ProfileContextMixin(ContextMixin, View):
    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.profile = (
            TrackerProfile.objects.get_or_create(user=request.user)
            if request.user and request.user.is_authenticated
            else None
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context
