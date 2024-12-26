from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.models.profiles import TrackerProfile
from terminusgps_tracker.forms import AssetCommandExecutionForm


class AssetRemoteView(LoginRequiredMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Remote",
        "legal_name": settings.TRACKER_PROFILE["LEGAL_NAME"],
    }
    http_method_names = ["get", "post"]
    form_class = AssetCommandExecutionForm
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    template_name = "terminusgps_tracker/assets/remote.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.asset = self.profile.assets.filter().get(pk=self.kwargs["id"])
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            self.asset.save(session)

    def get_success_url(self) -> str:
        return reverse("asset remote", kwargs={"id": self.asset.id})

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["asset"] = self.asset
        context["title"] = f"{self.asset.name} Remote"
        context["current_url"] = self.get_success_url()
        return context

    def form_valid(self, form: AssetCommandExecutionForm) -> HttpResponseRedirect:
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            session.wialon_api.unit_exec_cmd(
                **{
                    "itemId": self.asset.id,
                    "commandName": form.cleaned_data["command"].name,
                    "linkType": form.cleaned_data["command"].type,
                    "param": {},
                    "timeout": 5,
                    "flags": 0,
                }
            )
        return HttpResponseRedirect(self.get_success_url())
