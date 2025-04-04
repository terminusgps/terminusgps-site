from typing import Any

from authorizenet import apicontractsv1
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from terminusgps.authorizenet.utils import ControllerExecutionError

from terminusgps_tracker.forms import CustomerSubscriptionUpdateForm
from terminusgps_tracker.models.customers import Customer
from terminusgps_tracker.models.subscriptions import (
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
        initial["tier"] = SubscriptionTier.objects.get(
            pk=self.request.GET.get("tier") or 1
        )
        customer: Customer = self.get_object().customer
        if customer.addresses.filter().exists():
            initial["address"] = customer.addresses.filter().first()
        if customer.payments.filter().exists():
            initial["payment"] = customer.payments.filter().last()
        return initial

    def form_valid(self, form: CustomerSubscriptionUpdateForm) -> HttpResponse:
        if form.cleaned_data["payment"] is None:
            form.add_error(
                None,
                ValidationError(
                    _("Please add at least one payment method before proceeding.")
                ),
            )
            return self.form_invalid(form=form)
        if form.cleaned_data["address"] is None:
            form.add_error(
                None,
                ValidationError(
                    _("Please add at least one shipping address before proceeding.")
                ),
            )
            return self.form_invalid(form=form)

        try:
            subscription: CustomerSubscription = self.get_object()
            new_tier: SubscriptionTier = form.cleaned_data["tier"]

            if subscription.authorizenet_id is None:
                subscription.authorizenet_create_subscription()
            elif subscription.authorizenet_id:
                params = self.generate_update_params(
                    new_tier=new_tier,
                    address_id=form.cleaned_data["address"].authorizenet_id,
                    payment_id=form.cleaned_data["payment"].authorizenet_id,
                )
                profile = subscription.authorizenet_get_subscription_profile()
                profile.update(params)
        except ControllerExecutionError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
        else:
            subscription.tier = form.cleaned_data["tier"]
            subscription.payment = form.cleaned_data["payment"]
            subscription.address = form.cleaned_data["address"]
            subscription.save()
            return super().form_valid(form=form)

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()

    def generate_update_params(
        self,
        new_tier: SubscriptionTier,
        address_id: int | None = None,
        payment_id: int | None = None,
    ) -> apicontractsv1.ARBSubscriptionType:
        subscription = self.get_object()
        new_subscription = apicontractsv1.ARBSubscriptionType()
        new_profile = apicontractsv1.customerProfileIdType(
            customerProfileId=str(subscription.customer.authorizenet_id)
        )

        if subscription.tier != new_tier:
            # Update new name and amount
            name = f"{subscription.customer}'s {new_tier.name} Subscription"
            new_subscription.name = name
            new_subscription.amount = new_tier.amount

        if address_id and subscription.address.authorizenet_id != address_id:
            # Update new shipping address
            new_profile.customerAddressId = str(address_id)
            new_subscription.profile = new_profile

        if payment_id and subscription.payment.authorizenet_id != payment_id:
            # Update new payment method
            new_profile.customerPaymentProfileId = str(payment_id)
            new_subscription.profile = new_profile

        return new_subscription


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
