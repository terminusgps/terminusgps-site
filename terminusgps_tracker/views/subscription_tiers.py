from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    DeleteView,
    UpdateView,
)

from terminusgps_tracker.models import TrackerSubscriptionTier
from terminusgps_tracker.views.base import TrackerBaseView


class TrackerSubscriptionTierListView(ListView, TrackerBaseView):
    model = TrackerSubscriptionTier
    context_object_name = "tiers"
    ordering = "amount"
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )


class TrackerSubscriptionTierDetailView(DetailView, TrackerBaseView):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )


class TrackerSubscriptionTierCreateView(CreateView, TrackerBaseView):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )


class TrackerSubscriptionTierDeleteView(DeleteView, TrackerBaseView):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )


class TrackerSubscriptionTierUpdateView(UpdateView, TrackerBaseView):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/update.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_update.html"
    )
