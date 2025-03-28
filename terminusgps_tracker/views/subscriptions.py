from typing import Any

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from terminusgps_tracker.forms import CustomerSubscriptionUpdateForm
from terminusgps_tracker.models import CustomerSubscription
from terminusgps_tracker.models.subscriptions import SubscriptionTier
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
)


class SubscriptionTierListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = SubscriptionTier
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_tier_list.html"
    template_name = "terminusgps_tracker/subscriptions/tier_list.html"
    extra_context = {"class": "flex flex-col gap-4", "title": "Subscription Tiers"}
    context_object_name = "tier_list"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["subscription"] = (
            CustomerSubscription.objects.get(customer__user=self.request.user)
            if self.request.user and self.request.user.is_authenticated
            else None
        )
        return context


class CustomerSubscriptionDetailView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get", "patch"]
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_detail.html"
    template_name = "terminusgps_tracker/subscriptions/detail.html"
    extra_context = {"class": "flex flex-col gap-4 border p-4 rounded bg-white"}
    queryset = CustomerSubscription.objects.none()
    context_object_name = "subscription"

    def get_object(self, queryset=None) -> CustomerSubscription | None:
        return (
            CustomerSubscription.objects.get(customer__user=self.request.user)
            if self.request.user and self.request.user.is_authenticated
            else None
        )


class CustomerSubscriptionUpdateView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    extra_context = {"title": "Update Subscription", "class": "flex flex-col gap-4"}
    form_class = CustomerSubscriptionUpdateForm
    http_method_names = ["get", "post"]
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_update.html"
    template_name = "terminusgps_tracker/subscriptions/update.html"
    context_object_name = "subscription"

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        if self.request.GET.get("tier"):
            initial["tier"] = SubscriptionTier.objects.get(
                pk=self.request.GET.get("tier")
            )
        return initial

    def form_valid(self, form: CustomerSubscriptionUpdateForm) -> HttpResponse:
        print(f"{form.cleaned_data["tier"] = }")
        # TODO: upgrade/downgrade subscription
        return super().form_valid(form=form)

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()


class CustomerSubscriptionDeleteView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get", "post"]
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_delete.html"
    template_name = "terminusgps_tracker/subscriptions/delete.html"
    context_object_name = "subscription"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form: forms.Form) -> HttpResponse | HttpResponseRedirect:
        if self.get_object() is None:
            return self.form_invalid(form=form)

        subscription_profile = self.get_object().authorizenet_get_subscription_profile()
        subscription_profile.cancel()
        return super().form_valid(form=form)

    def get_object(self, queryset=None) -> CustomerSubscription | None:
        return (
            CustomerSubscription.objects.get(customer__user=self.request.user)
            if self.request.user and self.request.user.is_authenticated
            else None
        )
