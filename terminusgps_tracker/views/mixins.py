from typing import Callable

from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

from terminusgps_tracker.models import TrackerProfile


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
