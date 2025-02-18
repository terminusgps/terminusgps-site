from typing import Any, Callable

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from terminusgps_tracker.models import TrackerProfile

if not hasattr(settings, "TRACKER_APP_CONFIG"):
    raise ImproperlyConfigured("'TRACKER_APP_CONFIG' setting is required.")


class TrackerAppConfigContextMixin(ContextMixin):
    """Adds a tracker app configuration into the view context."""

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["tracker_config"] = settings.TRACKER_APP_CONFIG
        return context


class TrackerProfileSingleObjectMixin(SingleObjectMixin):
    def get_object(self) -> Any | None:
        if isinstance(self, CreateView):
            return None
        return super().get_object()

    def get_queryset(self) -> QuerySet:
        if not hasattr(self, "profile"):
            raise ValueError("'profile' was not set")
        if not hasattr(self, "model"):
            raise ValueError("'model' was not set")

        if self.profile is not None:
            return self.model.objects.filter(profile=self.profile)
        return self.model.objects.none()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        return super().get_context_data(**kwargs)


class TrackerProfileMultipleObjectMixin(MultipleObjectMixin):
    def get_queryset(self) -> QuerySet:
        if not hasattr(self, "profile"):
            raise ValueError("'profile' was not set")
        if not hasattr(self, "model"):
            raise ValueError("'model' was not set")

        if self.profile is not None:
            return self.model.objects.filter(profile=self.profile)
        return self.model.objects.none()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object_list = self.get_queryset().order_by(self.get_ordering())
        return super().get_context_data(**kwargs)


class TrackerProfileHasPaymentMethodTest(UserPassesTestMixin):
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please add a payment method and try again."

    def get_test_func(self) -> Callable:
        def user_has_payment_method() -> bool:
            if self.request.user:
                profile = TrackerProfile.objects.get(user=self.request.user)
                return profile.payments.exists()
            return False

        return user_has_payment_method


class TrackerProfileHasShippingAddressTest(UserPassesTestMixin):
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please add a shipping address and try again."

    def get_test_func(self) -> Callable:
        def user_has_shipping_address() -> bool:
            if self.request.user:
                profile = TrackerProfile.objects.get(user=self.request.user)
                return profile.addresses.exists()
            return False

        return user_has_shipping_address


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Sorry, you are not allowed to access this."

    def get_test_func(self) -> Callable:
        def user_is_staff() -> bool:
            if self.request.user and self.request.user.is_authenticated:
                return self.request.user.is_staff
            return False

        return user_is_staff


class SubscriptionRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("tracker login")
    permission_denied_message = "Please activate a subscription to perform this action."

    def get_test_func(self) -> Callable:
        def user_is_subscribed() -> bool:
            if self.request.user and self.request.user.is_authenticated:
                profile = TrackerProfile.objects.get(user=self.request.user)
                return (
                    profile.subscription.status.lower() == "active"
                    or self.request.user.is_staff
                )
            return False

        return user_is_subscribed
