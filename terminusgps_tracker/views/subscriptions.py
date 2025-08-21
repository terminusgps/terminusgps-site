import decimal

from authorizenet import apicontractsv1
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, FormView
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

    def get_success_url(self, unit_pk: int) -> str:
        return reverse(
            "tracker:detail unit",
            kwargs={
                "customer_pk": self.kwargs["customer_pk"],
                "unit_pk": unit_pk,
            },
        )

    def form_valid(
        self, form: CustomerSubscriptionCreationForm
    ) -> HttpResponse:
        customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
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
                amount=customer.calculate_subscription_amount(),
                trailAmount=decimal.Decimal("0.00"),
                profile=apicontractsv1.customerProfileIdType(
                    customerProfileId=customer.authorizenet_profile_id,
                    customerPaymentProfileId=form.cleaned_data["payment"].pk,
                    customerAddressId=form.cleaned_data["address"].pk,
                ),
            )
        )
        CustomerSubscription.objects.create(
            id=int(response.subscriptionId),
            customer=customer,
            payment=form.cleaned_data["payment"],
            address=form.cleaned_data["address"],
        )
        return super().form_valid(form=form)


class CustomerSubscriptionUpdateView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    form_class = CustomerSubscriptionUpdateForm
    http_method_names = ["get", "post"]

    def get_success_url(self, unit_pk: int) -> str:
        return reverse(
            "tracker:detail unit",
            kwargs={
                "customer_pk": self.kwargs["customer_pk"],
                "unit_pk": unit_pk,
            },
        )

    def form_valid(self, form: CustomerSubscriptionUpdateForm) -> HttpResponse:
        return super().form_valid(form=form)


class CustomerSubscriptionDetailView(
    CustomerAuthenticationRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    model = CustomerSubscription
    queryset = CustomerSubscription.objects.none()

    def get_queryset(
        self,
    ) -> QuerySet[CustomerSubscription, CustomerSubscription]:
        return CustomerSubscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        )
