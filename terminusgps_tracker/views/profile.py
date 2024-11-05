from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from terminusgps_tracker.models.customer import TrackerProfile
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items import WialonUnit


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile.html"
    extra_context = {"subtitle": settings.TRACKER_MOTD}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if (
            self.request.user.is_authenticated
            and TrackerProfile.objects.filter(user=self.request.user).exists()
        ):
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        else:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        if self.profile:
            context["title"] = f"{self.profile.user.first_name}'s Profile"
        return context


class TrackerProfileSubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile_subscription.html"
    extra_context = {"title": "Subscription", "subtitle": settings.TRACKER_MOTD}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if (
            self.request.user.is_authenticated
            and TrackerProfile.objects.filter(user=self.request.user).exists()
        ):
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        else:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context


class TrackerProfilePaymentsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile_payments.html"
    extra_context = {"title": "Payments", "subtitle": settings.TRACKER_MOTD}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if (
            self.request.user.is_authenticated
            and TrackerProfile.objects.filter(user=self.request.user).exists()
        ):
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        else:
            self.profile = None

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context


class TrackerProfileAssetsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile_assets.html"
    extra_context = {"title": "Assets", "subtitle": settings.TRACKER_MOTD}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if (
            self.request.user.is_authenticated
            and TrackerProfile.objects.filter(user=self.request.user).exists()
        ):
            self.profile = TrackerProfile.objects.get(user=self.request.user)
        else:
            self.profile = None

    def get_unit_info(self, unit_id: str) -> dict:
        with WialonSession() as session:
            unit = WialonUnit(id=unit_id, session=session)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context
