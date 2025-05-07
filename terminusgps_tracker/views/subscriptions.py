import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import CustomerSubscriptionUpdateForm
from terminusgps_tracker.models import Customer, CustomerSubscription, SubscriptionTier
from terminusgps_tracker.views.mixins import TrackerAppConfigContextMixin


class SubscriptionTierListView(
    HtmxTemplateResponseMixin, TrackerAppConfigContextMixin, ListView
):
    content_type = "text/html"
    extra_context = {
        "title": "Subscription Plans",
        "subtitle": "We have a plan for your plan",
        "class": "flex flex-col gap-4",
    }
    context_object_name = "tier_list"
    http_method_names = ["get"]
    model = SubscriptionTier
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_tier_list.html"
    template_name = "terminusgps_tracker/subscriptions/tier_list.html"


class CustomerSubscriptionTransactionsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {
        "title": "Subscription Transactions",
        "class": "flex flex-col gap-4",
    }
    http_method_names = ["get"]
    login_url = reverse_lazy("login")
    model = CustomerSubscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_transactions.html"
    )
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/transactions.html"

    def get_object(self, queryset=None) -> CustomerSubscription:
        customer, _ = Customer.objects.get_or_create(user=self.request.user)
        subscription, _ = CustomerSubscription.objects.get_or_create(customer=customer)
        return subscription

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        transactions = (
            self.get_object().authorizenet_get_subscription_profile().transactions
        )
        context["transaction_list"] = [
            {
                "response": str(t.response),
                "submitTimeUTC": parse_datetime(str(t.submitTimeUTC)),
                "payNum": int(t.payNum),
                "attemptNum": int(t.attemptNum),
            }
            for t in transactions
            if transactions
        ]
        return context


class CustomerSubscriptionDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    extra_context = {
        "class": "flex flex-col gap-4 border p-4 rounded bg-white dark:bg-terminus-gray-700 dark:border-terminus-gray-500"
    }
    context_object_name = "subscription"
    http_method_names = ["get", "patch"]
    login_url = reverse_lazy("login")
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_detail.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/detail.html"

    def get_object(self, queryset=None) -> CustomerSubscription | None:
        return (
            CustomerSubscription.objects.get(customer__user=self.request.user)
            if self.request.user and self.request.user.is_authenticated
            else None
        )


class CustomerSubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = {
        "title": "Update Subscription",
        "class": "flex flex-col gap-4 border p-4 rounded bg-white dark:bg-terminus-gray-700 dark:border-terminus-gray-500",
    }
    form_class = CustomerSubscriptionUpdateForm
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_update.html"
    permission_denied_message = "You do not have permission to view this."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/update.html"

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        form.fields["tier"].widget.choices = [
            (tier.pk, _(f"{tier.name} - ${tier.amount}/mo"))
            for tier in SubscriptionTier.objects.all()[:3]
        ]
        return form

    def get_object(self, queryset=None) -> CustomerSubscription:
        return CustomerSubscription.objects.get(customer__user=self.request.user)

    def get_initial(self) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial()
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
        if any(
            [
                subscription.tier != form.cleaned_data["tier"],
                subscription.address != form.cleaned_data["address"],
                subscription.payment != form.cleaned_data["payment"],
            ]
        ):
            subscription.tier = form.cleaned_data["tier"]
            subscription.address = form.cleaned_data["address"]
            subscription.payment = form.cleaned_data["payment"]
            subscription.save()
            subscription.authorizenet_update_subscription()
        else:
            subscription.tier = form.cleaned_data["tier"]
            subscription.address = form.cleaned_data["address"]
            subscription.payment = form.cleaned_data["payment"]
            subscription.save()
        return super().form_valid(form=form)

    def get_success_url(self) -> str:
        return self.get_object().get_absolute_url()


class CustomerSubscriptionDeleteView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = {"class": "flex flex-col gap-4"}
    http_method_names = ["get", "post"]
    login_url = reverse_lazy("login")
    model = CustomerSubscription
    partial_template_name = "terminusgps_tracker/subscriptions/partials/_delete.html"
    permission_denied_message = "Please login in order to view this content."
    raise_exception = False
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_tracker/subscriptions/delete.html"

    def get_object(self, queryset=None) -> CustomerSubscription:
        return CustomerSubscription.objects.get(customer__user=self.request.user)
