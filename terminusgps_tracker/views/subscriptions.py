from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from terminusgps_tracker.forms import CustomerSubscriptionUpdateForm
from terminusgps_tracker.models.customers import Customer
from terminusgps_tracker.models.subscriptions import (
    CustomerSubscription,
    SubscriptionTier,
)
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
)


class CustomerSubscriptionTransactionsView(
    CustomerRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = CustomerSubscription
    template_name = "terminusgps_tracker/subscriptions/transactions.html"
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_transactions.html"
    )
    extra_context = {
        "title": "Subscription Transactions",
        "class": "flex flex-col gap-4",
    }

    def get_object(self, queryset=None) -> CustomerSubscription:
        customer: Customer = Customer.objects.get(user=self.request.user)
        subscription, _ = CustomerSubscription.objects.get_or_create(customer=customer)
        return subscription

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        total_transactions = int(request.GET.get("total_transactions", 5))
        subscription_profile = self.get_object().authorizenet_get_subscription_profile()
        return super().get(request, *args, **kwargs)


class SubscriptionTierListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    http_method_names = ["get"]
    model = SubscriptionTier
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_tier_list.html"
    template_name = "terminusgps_tracker/subscriptions/tier_list.html"
    extra_context = {
        "title": "Subscription Tiers",
        "subtitle": "We have a plan for your plan...",
        "class": "flex flex-col gap-4",
    }
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
    extra_context = {
        "title": "Update Subscription",
        "class": "flex flex-col gap-4 border p-4 rounded bg-white",
    }
    form_class = CustomerSubscriptionUpdateForm
    http_method_names = ["get", "post"]
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_update.html"
    template_name = "terminusgps_tracker/subscriptions/update.html"
    context_object_name = "subscription"

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["tier"] = SubscriptionTier.objects.get(
            pk=self.request.GET.get("tier") or 1
        )
        customer = Customer.objects.get(user=self.request.user)
        if customer.addresses.filter().exists():
            initial["address"] = customer.addresses.filter().first()
        if customer.payments.filter().exists():
            initial["payment"] = customer.payments.filter().first()
        return initial

    def form_valid(self, form: CustomerSubscriptionUpdateForm) -> HttpResponse:
        new_tier = form.cleaned_data["tier"]
        address = form.cleaned_data["address"]
        payment = form.cleaned_data["payment"]

        if not payment:
            form.add_error(
                None,
                ValidationError(
                    _("Please add at least one payment method before proceeding.")
                ),
            )
            return self.form_invalid(form=form)
        if not address:
            form.add_error(
                None,
                ValidationError(
                    _("Please add at least one shipping address before proceeding.")
                ),
            )
            return self.form_invalid(form=form)

        subscription = self.get_object()
        subscription.payment = payment
        subscription.address = address
        subscription.tier = new_tier
        subscription.save()
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

        if self.get_object().authorizenet_id is not None:
            subscription_profile = (
                self.get_object().authorizenet_get_subscription_profile()
            )
            subscription_profile.cancel()
        return super().form_valid(form=form)

    def get_object(self, queryset=None) -> CustomerSubscription | None:
        return (
            CustomerSubscription.objects.get(customer__user=self.request.user)
            if self.request.user and self.request.user.is_authenticated
            else None
        )
