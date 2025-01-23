from typing import Any, Callable

from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from terminusgps_tracker.models import TrackerProfile


class TrackerProfileSingleObjectMixin(SingleObjectMixin):
    def get_object(self) -> Any | None:
        if not isinstance(self, CreateView):
            return super().get_object()
        return None

    def get_queryset(self) -> QuerySet:
        if not hasattr(self, "profile"):
            raise ValueError("'profile' was not set")

        if self.profile:
            return self.model.objects.filter(profile=self.profile)
        return self.model.objects.none()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        return super().get_context_data(**kwargs)


class TrackerProfileMultipleObjectMixin(MultipleObjectMixin):
    def get_queryset(self) -> QuerySet:
        if not hasattr(self, "profile"):
            raise ValueError("'profile' was not set")

        if self.profile:
            return self.model.objects.filter(profile=self.profile)
        return self.model.objects.none()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object_list = self.get_queryset().order_by(self.get_ordering())
        return super().get_context_data(**kwargs)


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
                    profile.subscription.status.upper() == "ACTIVE"
                    or self.request.user.is_staff
                )
            return False

        return user_is_subscribed
