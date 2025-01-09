from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from terminusgps_tracker.views.mixins import HtmxMixin, ProfileContextMixin
from terminusgps_tracker.models import (
    TrackerProfile,
    TrackerSubscription,
    TrackerAsset,
    TrackerShippingAddress,
    TrackerPaymentMethod,
)


class TrackerProfileView(
    TemplateView, LoginRequiredMixin, ProfileContextMixin, HtmxMixin
):
    content_type = "text/html"
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please login and try again."
    extra_context = {
        "title": "Your Profile",
        "subtitle": settings.TRACKER_PROFILE["MOTD"],
    }
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_profile.html"
    template_name = "terminusgps_tracker/profile.html"

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


class TrackerProfileSettingsView(TemplateView, ProfileContextMixin, HtmxMixin):
    extra_context = {
        "title": "Settings",
        "subtitle": "You can have up to 4 shipping addresses and up to 4 payment methods.",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_settings.html"
    template_name = "terminusgps_tracker/settings.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.profile is not None:
            context["addresses"] = self.get_addresses(self.profile, total=4)
            context["payments"] = self.get_payments(self.profile, total=4)
        return context

    @staticmethod
    def get_payments(profile: TrackerProfile, total: int = 4) -> QuerySet:
        if not profile.payments.exists() or profile.payments.count() == 0:
            return TrackerPaymentMethod.objects.none()
        return profile.payments.filter()[:total]

    @staticmethod
    def get_addresses(profile: TrackerProfile, total: int = 4) -> QuerySet:
        if not profile.addresses.exists() or profile.addresses.count() == 0:
            return TrackerShippingAddress.objects.none()
        return profile.addresses.filter()[:total]
