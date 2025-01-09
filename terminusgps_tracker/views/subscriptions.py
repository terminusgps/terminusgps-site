from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    TemplateView,
    UpdateView,
)

from terminusgps_tracker.models import TrackerSubscription
from terminusgps_tracker.views.mixins import (
    HtmxMixin,
    ProfileContextMixin,
    ProfileRequiredMixin,
)


class TrackerSubscriptionBaseView(
    TemplateView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    """Base Subscription View"""

    model = TrackerSubscription

    def get_object(self) -> TrackerSubscription:
        assert self.profile.subscription is not None
        return self.profile.subscription


class TrackerSubscriptionDeleteView(DeleteView, TrackerSubscriptionBaseView):
    template_name = "terminusgps_tracker/subscription/delete.html"
    partial_template_name = "terminusgps_tracker/subscription/partials/_delete.html"


class TrackerSubscriptionCreateView(CreateView, TrackerSubscriptionBaseView):
    template_name = "terminusgps_tracker/subscription/create.html"
    partial_template_name = "terminusgps_tracker/subscription/partials/_create.html"


class TrackerSubscriptionDetailView(DetailView, TrackerSubscriptionBaseView):
    template_name = "terminusgps_tracker/subscription/detail.html"
    partial_template_name = "terminusgps_tracker/subscription/partials/_detail.html"


class TrackerSubscriptionUpdateView(UpdateView, TrackerSubscriptionBaseView):
    template_name = "terminusgps_tracker/subscription/update.html"
    partial_template_name = "terminusgps_tracker/subscription/partials/_update.html"
