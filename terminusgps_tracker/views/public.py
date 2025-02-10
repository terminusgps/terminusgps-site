from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, RedirectView


from terminusgps_tracker.forms import BugReportForm
from terminusgps_tracker.views.base import TrackerBaseView


class WialonAddressSearchView(TrackerBaseView):
    http_method_names = ["post"]
    template_name = "terminusgps_tracker/search_address.html"
    partial_template_name = "terminusgps_tracker/partials/_search_address.html"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        base_url = (
            "https://search-maps.wialon.com/hst-api.wialon.com/gis_searchintelli?"
        )
        params = {}
        print(f"{request.POST = }")
        print(f"{request.POST.get("address") = }")
        return HttpResponse(status=200)


class TrackerMapView(TrackerBaseView):
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/map.html"
    partial_template_name = "terminusgps_tracker/partials/_map.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self._base_url = (
            "http://hst-api.wialon.com/avl_render/%(x)s_%(y)s_%(z)s/%(sid)s.png"
        )
        return super().setup(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        map_url = self._base_url % {
            "x": self.kwargs["x"],
            "y": self.kwargs["y"],
            "z": self.kwargs["zoom"],
            "sid": self.kwargs["sid"],
        }
        return self.render_to_response(context=self.get_context_data(map_url))

    def get_context_data(self, map_url: str | None = None, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["map_url"] = map_url
        return context


class TrackerLandingView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = reverse_lazy("tracker about")


class TrackerSourceView(RedirectView):
    http_method_names = ["get"]
    permanent = True
    url = settings.TRACKER_APP_CONFIG["REPOSITORY_URL"]


class TrackerAboutView(TrackerBaseView):
    extra_context = {"title": "About", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/about.html"
    partial_template_name = "terminusgps_tracker/partials/_about.html"


class TrackerPrivacyView(TrackerBaseView):
    extra_context = {"title": "Privacy Policy"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/privacy.html"
    partial_template_name = "terminusgps_tracker/partials/_privacy.html"


class TrackerContactView(TrackerBaseView):
    content_type = "text/html"
    extra_context = {"title": "Contact", "subtitle": "Ready to get in touch?"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/contact.html"
    partial_template_name = "terminusgps_tracker/partials/_contact.html"


class TrackerBugReportView(LoginRequiredMixin, FormView, TrackerBaseView):
    content_type = "text/html"
    extra_context = {
        "title": "Bug Report",
        "subtitle": "Found a bug?",
        "class": "flex flex-col gap-2 p-4 bg-gray-300 rounded caret-terminus-red-600 border border-gray-600",
    }
    form_class = BugReportForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_bug_report.html"
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/bug_report.html"
    login_url = reverse_lazy("login")
    raise_exception = False
    permission_denied_message = "Please login and try again."

    def get_initial(self) -> dict[str, Any]:
        return {"user": self.request.user}
