from typing import Any
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    DeleteView,
    UpdateView,
)

from terminusgps_tracker.models import TrackerSubscriptionTier
from terminusgps_tracker.views.base import TrackerBaseView
from terminusgps_tracker.views.mixins import (
    TrackerProfileSingleObjectMixin,
    TrackerProfileMultipleObjectMixin,
)


class TrackerSubscriptionTierListView(
    ListView, TrackerBaseView, TrackerProfileMultipleObjectMixin
):
    model = TrackerSubscriptionTier
    context_object_name = "tiers"
    ordering = "amount"
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )


class TrackerSubscriptionTierDetailView(
    DetailView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )


class TrackerSubscriptionTierCreateView(
    CreateView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = None
        return super().get_context_data(**kwargs)


class TrackerSubscriptionTierDeleteView(
    DeleteView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )


class TrackerSubscriptionTierUpdateView(
    UpdateView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/update.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_update.html"
    )
