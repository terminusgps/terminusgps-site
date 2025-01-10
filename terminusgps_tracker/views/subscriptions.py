from typing import Any

from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, UpdateView
from django.core.exceptions import ValidationError

from terminusgps_tracker.models import TrackerSubscription
from terminusgps_tracker.forms import SubscriptionUpdateForm, SubscriptionCancelForm
from terminusgps_tracker.views.mixins import (
    HtmxMixin,
    ProfileContextMixin,
    ProfileRequiredMixin,
)


class TrackerSubscriptionCancelView(
    FormView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    partial_template_name = "terminusgps_tracker/subscription/partials/_cancel.html"
    template_name = "terminusgps_tracker/subscription/cancel.html"
    form_class = SubscriptionCancelForm
    success_url = reverse_lazy("tracker profile")
    context_object_name = "subscription"

    def get_object(self, queryset: QuerySet | None = None) -> TrackerSubscription:
        return self.profile.subscription

    def get_success_url(self, subscription: TrackerSubscription | None = None) -> str:
        if subscription is not None:
            return reverse("subscription detail", kwargs={"pk": subscription.pk})
        return str(self.success_url)

    def form_valid(self, form: SubscriptionCancelForm) -> HttpResponse:
        subscription = TrackerSubscription.objects.get(pk=self.kwargs["pk"])
        subscription.cancel()
        return HttpResponseRedirect(self.get_success_url(subscription))


class TrackerSubscriptionDetailView(
    DetailView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_detail.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/detail.html"
    context_object_name = "subscription"
    extra_context = {
        "class": "rounded bg-white p-8 drop-shadow border-terminus-gray-600 border"
    }

    def get_object(self, queryset: QuerySet | None = None) -> TrackerSubscription:
        return self.profile.subscription


class TrackerSubscriptionUpdateView(
    UpdateView, ProfileContextMixin, ProfileRequiredMixin, HtmxMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_update.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/update.html"
    fields = ["tier", "payment_id", "address_id"]
    context_object_name = "subscription"
    extra_context = {
        "class": "rounded bg-white p-8 drop-shadow border-terminus-gray-600 border"
    }

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["address_id"] = (
            self.profile.addresses.filter(is_default=True).first().authorizenet_id
        )
        initial["payment_id"] = (
            self.profile.payments.filter(is_default=True).first().authorizenet_id
        )
        initial["tier"] = self.profile.subscription.tier
        return initial

    def get_object(self, queryset: QuerySet | None = None) -> TrackerSubscription:
        return self.profile.subscription

    def get_success_url(self, subscription: TrackerSubscription | None = None) -> str:
        if subscription is not None:
            return reverse("detail subscription", kwargs={"pk": subscription.pk})
        return str(self.success_url)

    def form_valid(self, form: SubscriptionUpdateForm) -> HttpResponse:
        subscription = self.get_object()
        new_tier = form.cleaned_data["tier"]
        payment_id = form.cleaned_data["payment_id"]
        address_id = form.cleaned_data["address_id"]
        upgrading = bool(
            subscription.tier is None or subscription.tier.amount < new_tier.amount
        )

        try:
            subscription.upgrade(
                new_tier=new_tier, payment_id=payment_id, address_id=address_id
            ) if upgrading else subscription.downgrade(
                new_tier=new_tier, payment_id=payment_id, address_id=address_id
            )
        except ValueError as e:
            print(e)
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end. Please try again later."
                    ),
                    code="invalid",
                ),
            )
        else:
            subscription.save()
        return HttpResponseRedirect(self.get_success_url(subscription))
