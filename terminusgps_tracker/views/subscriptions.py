from django.db.models import QuerySet
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from terminusgps_tracker.models import TrackerSubscription
from terminusgps_tracker.views.mixins import (
    HtmxMixin,
    ProfileContextMixin,
    ProfileRequiredMixin,
)


class TrackerSubscriptionDeleteView(
    DeleteView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_delete.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/delete.html"


class TrackerSubscriptionCreateView(
    CreateView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_create.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/create.html"


class TrackerSubscriptionDetailView(
    DetailView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_detail.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/detail.html"

    def get_object(
        self, queryset: QuerySet | None = None
    ) -> TrackerSubscription | None:
        if self.profile is not None:
            return self.profile.subscription


class TrackerSubscriptionUpdateView(
    UpdateView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_update.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/update.html"
