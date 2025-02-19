from typing import Any

from django.db.models import QuerySet
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, UpdateView
from django.core.exceptions import ValidationError

from terminusgps_tracker.models import TrackerSubscription, TrackerSubscriptionTier
from terminusgps_tracker.forms import SubscriptionUpdateForm, SubscriptionCancelForm
from terminusgps_tracker.views.base import TrackerBaseView
from terminusgps_tracker.views.mixins import TrackerProfileSingleObjectMixin


class TrackerSubscriptionCancelView(
    FormView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    http_method_names = ["get", "post"]
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
    DetailView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_detail.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/detail.html"
    context_object_name = "subscription"
    extra_context = {"class": "rounded bg-gray-100 p-8 shadow border-gray-600 border"}

    def get_object(self, queryset: QuerySet | None = None) -> TrackerSubscription:
        return self.profile.subscription

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        self.object = self.get_object()
        context: dict[str, Any] = super().get_context_data(**kwargs)
        if self.object.tier is not None:
            context["features"] = self.object.tier.features.all()
        return context


class TrackerSubscriptionUpdateView(
    UpdateView, TrackerBaseView, TrackerProfileSingleObjectMixin
):
    model = TrackerSubscription
    partial_template_name = "terminusgps_tracker/subscription/partials/_update.html"
    queryset = TrackerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscription/update.html"
    form_class = SubscriptionUpdateForm
    context_object_name = "subscription"
    extra_context = {
        "class": "rounded bg-gray-100 p-8 shadow border-gray-600 border gap-4"
    }

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if not self.profile.payments.exists():
            messages.add_message(
                request,
                messages.WARNING,
                _("Please add a payment method before proceeding."),
                extra_tags="block w-full bg-red-100 p-2 text-terminus-red-800 text-center",
            )
        if not self.profile.addresses.exists():
            messages.add_message(
                request,
                messages.WARNING,
                _("Please add a shipping address before proceeding."),
                extra_tags="block w-full bg-red-100 p-2 text-terminus-red-800 text-center",
            )

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["tier"] = TrackerSubscriptionTier.objects.get(pk=2)
        if self.profile.payments.exists():
            initial["payment_id"] = self.profile.payments.filter(default=True).first()
        if self.profile.addresses.exists():
            initial["address_id"] = self.profile.addresses.filter(default=True).first()
        return initial

    def get_object(self, queryset: QuerySet | None = None) -> TrackerSubscription:
        return self.profile.subscription

    def get_success_url(self, subscription: TrackerSubscription | None = None) -> str:
        if subscription is not None:
            return reverse("subscription detail", kwargs={"pk": subscription.pk})
        return str(self.success_url)

    def form_valid(self, form: SubscriptionUpdateForm) -> HttpResponse:
        subscription = self.get_object()
        new_tier = form.cleaned_data["tier"]
        payment_id = form.cleaned_data["payment_id"]
        address_id = form.cleaned_data["address_id"]

        try:
            upgrading = bool(
                subscription.tier is None or subscription.tier.amount < new_tier.amount
            )

            if upgrading:
                subscription.upgrade(new_tier, payment_id, address_id)
            else:
                subscription.downgrade(new_tier, payment_id, address_id)
            subscription.save()
            return HttpResponseRedirect(self.get_success_url(subscription))
        except ValueError:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! Something went wrong on our end. Please try again later."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
