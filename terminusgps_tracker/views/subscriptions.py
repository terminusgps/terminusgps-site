from typing import Any

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from terminusgps_tracker.forms import CustomerSubscriptionUpdateForm
from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    CustomerSubscription,
    SubscriptionTier,
)
from terminusgps_tracker.views.mixins import (
    CustomerRequiredMixin,
    HtmxTemplateResponseMixin,
    TrackerAppConfigContextMixin,
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

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context: dict[str, Any] = super().get_context_data(**kwargs)
        context["transaction_list"] = (
            self.get_object().authorizenet_get_subscription_profile().transactions
        )
        return context


class SubscriptionTierListView(
    HtmxTemplateResponseMixin, TrackerAppConfigContextMixin, ListView
):
    content_type = "text/html"
    http_method_names = ["get"]
    model = SubscriptionTier
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_tier_list.html"
    template_name = "terminusgps_tracker/subscriptions/tier_list.html"
    extra_context = {
        "title": "Subscription Plans",
        "subtitle": "We have a plan for your plan",
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
    extra_context = {
        "class": "flex flex-col gap-4 border p-4 rounded bg-white dark:bg-terminus-gray-700 dark:border-terminus-gray-500"
    }
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
        "class": "flex flex-col gap-4 border p-4 rounded bg-white dark:bg-terminus-gray-700 dark:border-terminus-gray-500",
    }
    form_class = CustomerSubscriptionUpdateForm
    http_method_names = ["get", "post"]
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_update.html"
    template_name = "terminusgps_tracker/subscriptions/update.html"
    context_object_name = "subscription"

    def get_object(self, queryset=None) -> CustomerSubscription:
        return CustomerSubscription.objects.get(customer__user=self.request.user)

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        customer: Customer = self.get_object().customer
        addresses = customer.addresses.filter()
        payments = customer.payments.filter()

        if self.request.GET.get("tier"):
            initial["tier"] = self.request.GET.get("tier", 1)
        if addresses.exists():
            initial["address"] = addresses.filter(default=True).first()
        if payments.exists():
            initial["payment"] = payments.filter(default=True).first()
        return initial

    def form_valid(self, form: CustomerSubscriptionUpdateForm) -> HttpResponse:
        if not form.cleaned_data["tier"]:
            form.add_error(
                None,
                ValidationError(
                    _("Please select a subscription tier before proceeding.")
                ),
            )
            return self.form_invalid(form=form)
        if not form.cleaned_data["payment"]:
            form.add_error(
                None,
                ValidationError(
                    _("Please add at least one payment method before proceeding.")
                ),
            )
            return self.form_invalid(form=form)
        if not form.cleaned_data["address"]:
            form.add_error(
                None,
                ValidationError(
                    _("Please add at least one shipping address before proceeding.")
                ),
            )
            return self.form_invalid(form=form)

        subscription: CustomerSubscription = self.get_object()
        new_tier: SubscriptionTier = form.cleaned_data["tier"]
        new_address: CustomerShippingAddress = form.cleaned_data["address"]
        new_payment: CustomerPaymentMethod = form.cleaned_data["payment"]
        updated_fields: list = []
        if subscription.tier != new_tier:
            subscription.tier = new_tier
            updated_fields.append("tier")
        if subscription.address != new_address:
            subscription.address = new_address
            updated_fields.append("address")
        if subscription.payment != new_payment:
            subscription.payment = new_payment
            updated_fields.append("payment")
        subscription.save(update_fields=updated_fields)
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

    def get_object(self, queryset=None) -> CustomerSubscription:
        return CustomerSubscription.objects.get(customer__user=self.request.user)
