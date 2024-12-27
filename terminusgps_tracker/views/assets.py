from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.models.assets import TrackerAssetCommand
from terminusgps_tracker.models.profiles import TrackerProfile
from terminusgps_tracker.forms import CommandExecutionForm


class AssetMapView(LoginRequiredMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
    template_name = "terminusgps_tracker/assets/map.html"

    def get_success_url(self) -> str:
        return reverse("asset map", kwargs={"id": self.asset.id})

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.asset = self.profile.assets.filter().get(pk=self.kwargs["id"])

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        return super().get(request, *args, **kwargs)

    def post(
        self, request: HttpRequest, *args, **kwargs
    ) -> HttpResponseRedirect | HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        return super().post(request, *args, **kwargs)


class CommandExecutionView(LoginRequiredMixin, FormView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    form_class = CommandExecutionForm
    template_name = "terminusgps_tracker/assets/remote_button.html"
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True

    def get_success_url(self) -> str:
        return reverse("execute command", kwargs={"id": self.asset.id})

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        self.asset = self.profile.assets.filter().get(pk=self.kwargs["id"])

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        return super().post(request, *args, **kwargs)

    def form_valid(
        self, form: CommandExecutionForm
    ) -> HttpResponse | HttpResponseRedirect:
        command: TrackerAssetCommand = form.cleaned_data["command"]
        try:
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                command.execute(self.asset.id, session)
        except WialonError or ValueError:
            form.add_error(
                "command",
                ValidationError(
                    _("Whoops! We couldn't execute '%(cmd)s'. Please try again later."),
                    code="invalid",
                    params={"cmd": command.name},
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)


class AssetRemoteView(LoginRequiredMixin, TemplateView):
    content_type = "text/html"
    http_method_names = ["get"]
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
        context["commands"] = self.asset.commands.filter()
        return context
