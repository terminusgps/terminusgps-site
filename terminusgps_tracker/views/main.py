import decimal
import typing

from authorizenet import apicontractsv1
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
    Subscription,
)
from terminusgps_payments.services import AuthorizenetService

from terminusgps_tracker.forms import SubscriptionCreationForm
from terminusgps_tracker.models import Customer


class CustomerDashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_dashboard.html"
    template_name = "terminusgps_tracker/dashboard.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerAccountView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Account",
        "subtitle": "Your Terminus GPS account at a glance",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_account.html"
    template_name = "terminusgps_tracker/account.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerUnitsView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Units",
        "subtitle": "Your Terminus GPS units and what you can do with them",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_units.html"
    template_name = "terminusgps_tracker/units.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerSubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Your Subscription"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_tracker/partials/_subscription.html"
    template_name = "terminusgps_tracker/subscription.html"

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerSubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Subscription"}
    form_class = SubscriptionCreationForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/partials/_create_subscription.html"
    )
    template_name = "terminusgps_tracker/create_subscription.html"
    success_url = reverse_lazy("terminusgps_tracker:subscription")

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.anet_service = AuthorizenetService()
        try:
            CustomerProfile.objects.get(user=self.request.user)
        except CustomerProfile.DoesNotExist:
            customer_profile = CustomerProfile(user=self.request.user)
            resp = self.anet_service.create_customer_profile(customer_profile)
            customer_profile.pk = int(resp.customerProfileId)
            customer_profile.save()

    def form_valid(self, form: SubscriptionCreationForm) -> HttpResponse:
        try:
            customer = Customer.objects.get(user=self.request.user)
            customer_profile = CustomerProfile.objects.get(user=customer.user)
            address_profile = form.cleaned_data["address_profile"]
            payment_profile = form.cleaned_data["payment_profile"]

            subscription_name = "Terminus GPS Subscription"
            subscription_amount = customer.get_subscription_grand_total()
            subscription_schedule = apicontractsv1.paymentScheduleType()
            subscription_schedule.startDate = timezone.now()
            subscription_schedule.totalOccurrences = 9999
            subscription_schedule.trialOccurrences = 0
            subscription_schedule.interval = (
                apicontractsv1.paymentScheduleTypeInterval(
                    length=1, unit="months"
                )
            )

            anet_subscription = apicontractsv1.ARBSubscriptionType()
            anet_subscription.name = subscription_name
            anet_subscription.amount = subscription_amount
            anet_subscription.trialAmount = decimal.Decimal("0.00")
            anet_subscription.paymentSchedule = subscription_schedule
            anet_subscription.profile = apicontractsv1.customerProfileIdType(
                customerProfileId=str(customer_profile.pk),
                customerPaymentProfileId=str(payment_profile.pk),
                customerAddressId=str(address_profile.pk),
            )

            subscription = Subscription(
                id=None,
                name=subscription_name,
                amount=subscription_amount,
                customer_profile=customer_profile,
                address_profile=address_profile,
                payment_profile=payment_profile,
            )
            anet_response = self.anet_service.create_subscription(
                subscription, anet_subscription
            )
            subscription.pk = int(anet_response.subscriptionId)
            subscription.save()
            customer.subscription = subscription
            customer.save()
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("%(code)s: %(message)s"),
                            code="invalid",
                            params={"code": e.code, "message": e.message},
                        ),
                    )
            return self.form_invalid(form=form)

    def get_form(self, form_class=None) -> SubscriptionCreationForm:
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        payment_choices = self.get_payment_choices(payment_qs)
        address_choices = self.get_address_choices(address_qs)
        form.fields["payment_profile"].queryset = payment_qs
        form.fields["address_profile"].queryset = address_qs
        form.fields["payment_profile"].choices = payment_choices
        form.fields["address_profile"].choices = address_choices
        form.fields["payment_profile"].empty_label = None
        form.fields["address_profile"].empty_label = None
        return form

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer = Customer.objects.get(user=self.request.user)

        context["customer"] = customer
        context["subtotal"] = customer.get_subscription_subtotal()
        context["tax"] = context["subtotal"] * customer.tax_rate
        context["grand_total"] = customer.get_subscription_grand_total()
        return context

    @staticmethod
    def get_address_choices(qs) -> tuple[tuple]:
        return (
            (address_profile.pk, _(f"{address_profile.address.address}"))
            for address_profile in qs
        )

    @staticmethod
    def get_payment_choices(qs) -> tuple[tuple]:
        return (
            (
                payment_profile.pk,
                _(
                    f"{payment_profile.credit_card.cardType} ending in {str(payment_profile.credit_card.cardNumber)[-4:]}"
                ),
            )
            for payment_profile in qs
        )
