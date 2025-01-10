from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    DeleteView,
    UpdateView,
)

from terminusgps_tracker.models import TrackerSubscriptionTier
from terminusgps_tracker.views.mixins import HtmxMixin, ProfileContextMixin


class TrackerSubscriptionTierListView(ListView, ProfileContextMixin, HtmxMixin):
    model = TrackerSubscriptionTier
    context_object_name = "tiers"
    ordering = "amount"
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )


class TrackerSubscriptionTierDetailView(DetailView, ProfileContextMixin, HtmxMixin):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )

    def get_context_data(self, **kwargs):
        print(super().get_context_data(**kwargs))
        return super().get_context_data(**kwargs)


class TrackerSubscriptionTierCreateView(CreateView, ProfileContextMixin, HtmxMixin):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )


class TrackerSubscriptionTierDeleteView(DeleteView, ProfileContextMixin, HtmxMixin):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )


class TrackerSubscriptionTierUpdateView(UpdateView, ProfileContextMixin, HtmxMixin):
    model = TrackerSubscriptionTier
    template_name = "terminusgps_tracker/subscription_tier/update.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_update.html"
    )
