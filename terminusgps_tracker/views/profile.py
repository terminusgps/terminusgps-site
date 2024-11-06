from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from terminusgps_tracker.models.customer import TrackerProfile
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.items import WialonUnitGroup
from terminusgps_tracker.http import HttpRequest, HttpResponse


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile.html"
    extra_context = {"subtitle": settings.TRACKER_MOTD}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.htmx:
            with WialonSession() as session:
                return self.render_to_response(
                    context=self.get_context_data(session=session), **kwargs
                )
        return super().get(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if (
            self.request.user.is_authenticated
            and TrackerProfile.objects.filter(user=self.request.user).exists()
        ):
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        else:
            self.profile = None

    def get_context_data(
        self, session: WialonSession | None = None, **kwargs
    ) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Profile"
            if session:
                unit_group = WialonUnitGroup(
                    id=str(self.profile.wialon_group_id), session=session
                )
                context["wialon_units"] = unit_group.items
        return context
