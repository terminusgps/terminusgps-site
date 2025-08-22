import decimal
import typing

from authorizenet import apicontractsv1
from django import forms
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DeleteView, DetailView, FormView
from terminusgps.authorizenet import subscriptions as anet_subscriptions
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import (
    CustomerSubscriptionCreationForm,
    CustomerSubscriptionUpdateForm,
)
from terminusgps_tracker.models import Customer, CustomerSubscription
from terminusgps_tracker.views.mixins import (
    CustomerAuthenticationRequiredMixin,
)


class CustomerSubscriptionCreateView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = CustomerSubscriptionCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_create.html"
    )
    template_name = "terminusgps_tracker/subscriptions/create.html"

    def get_success_url(self, subscription: CustomerSubscription) -> str:
        return reverse(
            "tracker:detail subscription",
            kwargs={
                "customer_pk": self.kwargs["customer_pk"],
                "subscription_pk": subscription.pk,
            },
        )

    def form_valid(
        self, form: CustomerSubscriptionCreationForm
    ) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        payment = form.cleaned_data["payment"]
        address = form.cleaned_data["address"]
        response = anet_subscriptions.create_subscription(
            apicontractsv1.ARBSubscriptionType(
                name=f"{customer.user.first_name}'s Subscription",
                paymentSchedule=apicontractsv1.paymentScheduleType(
                    interval=apicontractsv1.paymentScheduleTypeInterval(
                        length=1,
                        unit=apicontractsv1.ARBSubscriptionUnitEnum.months,
                    ),
                    startDate=timezone.now(),
                    totalOccurrences=9999,
                    trialOccurrences=0,
                ),
                amount=...,  # Aggregate unit amounts
                trailAmount=decimal.Decimal("0.00"),
                profile=apicontractsv1.customerProfileIdType(
                    customerProfileId=str(customer.authorizenet_profile_id),
                    customerPaymentProfileId=str(payment.pk),
                    customerAddressId=str(address.pk),
                ),
            )
        )
        subscription = CustomerSubscription.objects.create(
            id=int(response.subscriptionId),
            customer=customer,
            payment=payment,
            address=address,
        )
        return HttpResponseRedirect(self.get_success_url(subscription))


class CustomerSubscriptionUpdateView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = CustomerSubscriptionUpdateForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_update.html"
    )
    template_name = "terminusgps_tracker/subscriptions/update.html"

    def get_initial(self) -> dict[str, typing.Any]:
        customer: Customer = Customer.objects.get(
            pk=self.kwargs["customer_pk"]
        )

        initial: dict[str, typing.Any] = super().get_initial()
        initial["address"] = customer.addresses.first()
        initial["payment"] = customer.payments.first()
        return initial

    def get_queryset(
        self,
    ) -> QuerySet[CustomerSubscription, CustomerSubscription]:
        return CustomerSubscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )

    def get_success_url(self) -> str:
        return reverse(
            "tracker:detail subscription",
            kwargs={
                "customer_pk": self.kwargs["customer_pk"],
                "subscription_pk": self.kwargs["subscription_pk"],
            },
        )

    def form_valid(self, form: CustomerSubscriptionUpdateForm) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
        payment = form.cleaned_data["payment"]
        address = form.cleaned_data["address"]
        response = anet_subscriptions.update_subscription(
            subscription_id=int(self.kwargs["subscription_pk"]),
            subscription_obj=apicontractsv1.ARBSubscriptionType(
                profile=apicontractsv1.customerProfileIdType(
                    customerProfileId=str(customer.authorizenet_profile_id),
                    customerPaymentProfileId=str(payment.pk),
                    customerAddressId=str(address.pk),
                )
            ),
        )
        return HttpResponseRedirect(self.get_success_url())


class CustomerSubscriptionDetailView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = {"title": "Subscription Details"}
    model = CustomerSubscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_detail.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = CustomerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscriptions/detail.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["profile"] = anet_subscriptions.get_subscription(
            subscription_id=int(self.kwargs["subscription_pk"]),
            include_transactions=True,
        )
        return context

    def get_queryset(
        self,
    ) -> QuerySet[CustomerSubscription, CustomerSubscription]:
        return CustomerSubscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )


class CustomerSubscriptionDeleteView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DeleteView
):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = {"title": "Delete Subscription"}
    http_method_names = ["get", "post"]
    model = CustomerSubscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_delete.html"
    )
    pk_url_kwarg = "subscription_pk"
    queryset = CustomerSubscription.objects.none()
    template_name = "terminusgps_tracker/subscriptions/delete.html"

    def form_valid(self, form: forms.Form) -> HttpResponse:
        anet_subscriptions.cancel_subscription(
            subscription_id=int(self.kwargs["subscription_pk"])
        )
        return super().form_valid(form=form)

    def get_success_url(self) -> str:
        return reverse(
            "tracker:account",
            kwargs={"customer_pk": self.kwargs["customer_pk"]},
        )
