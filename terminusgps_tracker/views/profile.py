from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from terminusgps_tracker.models import TrackerProfile, TrackerSubscription, TrackerAsset


class TrackerProfileView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/profile.html"
    extra_context = {
        "title": "Your Profile",
        "subtitle": settings.TRACKER_PROFILE["MOTD"],
    }
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = False
    http_method_names = ["get", "post"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        try:
            self.profile = (
                TrackerProfile.objects.get(user=request.user)
                if request.user and request.user.is_authenticated
                else None
            )
        except TrackerProfile.DoesNotExist:
            self.profile = (
                TrackerProfile.objects.create(user=request.user)
                if request.user and request.user.is_authenticated
                else None
            )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile is not None:
            context["title"] = f"{self.profile.user.first_name}'s Profile"
            context["assets"] = TrackerAsset.objects.filter(profile=self.profile)
            context["subscription"], _ = TrackerSubscription.objects.get_or_create(
                profile=self.profile
            )
        return context


class TrackerProfileSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "terminusgps_tracker/profile/settings.html"
    partial_template_name = "terminusgps_tracker/profile/partials/_settings.html"
    extra_context = {"title": "Settings"}
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    raise_exception = True
    http_method_names = ["get"]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.profile = TrackerProfile.objects.get(user=request.user)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["addresses"] = self.get_addresses(self.profile)
        context["payments"] = self.get_payments(self.profile)
        return context

    @staticmethod
    def get_payments(profile: TrackerProfile, total: int = 4) -> QuerySet:
        if profile.payments.count() == 0:
            return []
        return profile.payments.filter()[:total]

    @staticmethod
    def get_addresses(profile: TrackerProfile, total: int = 4) -> QuerySet:
        if profile.addresses.count() == 0:
            return []
        return profile.addresses.filter()[:total]
