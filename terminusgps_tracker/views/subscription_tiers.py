from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    DeleteView,
    UpdateView,
)

from terminusgps_tracker.models import TrackerSubscriptionTier
from terminusgps_tracker.views.mixins import HtmxMixin, ProfileContextMixin


class TrackerSubscriptionTierBaseView(TemplateView, ProfileContextMixin, HtmxMixin):
    model = TrackerSubscriptionTier


class TrackerSubscriptionTierListView(ListView, TrackerSubscriptionTierBaseView):
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )


class TrackerSubscriptionTierDetailView(DetailView, TrackerSubscriptionTierBaseView):
    template_name = "terminusgps_tracker/subscription_tier/detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_detail.html"
    )


class TrackerSubscriptionTierCreateView(CreateView, TrackerSubscriptionTierBaseView):
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )


class TrackerSubscriptionTierDeleteView(DeleteView, TrackerSubscriptionTierBaseView):
    template_name = "terminusgps_tracker/subscription_tier/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_create.html"
    )


class TrackerSubscriptionTierUpdateView(UpdateView, TrackerSubscriptionTierBaseView):
    template_name = "terminusgps_tracker/subscription_tier/update.html"
    partial_template_name = (
        "terminusgps_tracker/subscription_tier/partials/_update.html"
    )
