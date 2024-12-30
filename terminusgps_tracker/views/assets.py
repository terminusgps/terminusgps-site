from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.forms import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.models.assets import TrackerAsset, TrackerAssetCommand
from terminusgps_tracker.models.profiles import TrackerProfile
from terminusgps_tracker.forms import CommandExecutionForm


class AssetListView(LoginRequiredMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/assets/list.html"
    partial_name = "terminusgps_tracker/assets/partials/_list.html"
    model = TrackerAsset
    context_object_name = "asset_list"
    paginate_by = 6

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_queryset(self) -> QuerySet:
        if not self.profile.assets.exists() or self.profile.assets.all().count() < 0:
            return TrackerAsset.objects.none()
        return self.profile.assets.all()


class AssetDetailView(LoginRequiredMixin, DetailView):
    content_type = "text/html"
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/assets/detail.html"
    partial_name = "terminusgps_tracker/assets/partials/_detail.html"
    model = TrackerAsset
    context_object_name = "asset"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)

    def get_queryset(self) -> QuerySet:
        return self.profile.assets.all()


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/assets/update.html"
    partial_name = "terminusgps_tracker/assets/partials/_update.html"
    fields = ["name", "imei_number"]


class AssetCreationView(LoginRequiredMixin, CreateView):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/assets/create.html"
    partial_name = "terminusgps_tracker/assets/partials/_create.html"
    fields = ["name", "imei_number"]

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)


class AssetDeletionView(LoginRequiredMixin, DeleteView):
    content_type = "text/html"
    http_method_names = ["get", "delete"]
    template_name = "terminusgps_tracker/assets/delete.html"
    partial_name = "terminusgps_tracker/assets/partials/_delete.html"
    fields = ["id"]

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.headers.get("HX-Request"):
            return HttpResponse(status=402)
        self.template_name = self.partial_name
        return super().delete(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_name
        return super().get(request, *args, **kwargs)


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
