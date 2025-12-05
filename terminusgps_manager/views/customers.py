import decimal
import typing

from authorizenet import apicontractsv1
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import FormView, TemplateView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps_payments.models import (
    AddressProfile,
    PaymentProfile,
    Subscription,
)
from terminusgps_payments.services import AuthorizenetService

from .. import forms, models


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Dashboard"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/partials/_dashboard.html"
    template_name = "terminusgps_manager/dashboard.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.customer, _ = models.TerminusgpsCustomer.objects.get_or_create(
            user=request.user
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class AccountView(LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Account"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/partials/_account.html"
    template_name = "terminusgps_manager/account.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.customer, _ = models.TerminusgpsCustomer.objects.get_or_create(
            user=request.user
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class SubscriptionView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Subscription"}
    http_method_names = ["get"]
    partial_template_name = "terminusgps_manager/partials/_subscription.html"
    template_name = "terminusgps_manager/subscription.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.customer, _ = models.TerminusgpsCustomer.objects.get_or_create(
            user=request.user
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context


class SubscriptionCreateSuccessView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {"title": "Subscription Created"}
    http_method_names = ["get"]
    partial_template_name = (
        "terminusgps_manager/partials/_create_subscription_success.html"
    )
    template_name = "terminusgps_manager/create_subscription_success.html"


class SubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    extra_context = {"title": "Create Subscription"}
    form_class = forms.SubscriptionCreateForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_manager/partials/_create_subscription.html"
    )
    template_name = "terminusgps_manager/create_subscription.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.customer, _ = models.TerminusgpsCustomer.objects.get_or_create(
            user=request.user
        )
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["customer"] = self.customer
        return context

    def get_form(self, form_class=None) -> forms.SubscriptionCreateForm:
        form = super().get_form(form_class=form_class)
        payment_qs = PaymentProfile.objects.for_user(self.request.user)
        address_qs = AddressProfile.objects.for_user(self.request.user)
        pprofile_field = form.fields["payment_profile"]
        aprofile_field = form.fields["address_profile"]
        pprofile_field.queryset = payment_qs
        aprofile_field.queryset = address_qs
        pprofile_field.empty_label = None
        aprofile_field.empty_label = None
        return form

    @transaction.atomic
    def form_valid(self, form: forms.SubscriptionCreateForm) -> HttpResponse:
        try:
            customer_profile = getattr(self.customer.user, "customer_profile")
            payment_profile = form.cleaned_data["payment_profile"]
            address_profile = form.cleaned_data["address_profile"]
            start_date = timezone.now()
            name = "Terminus GPS"

            # Set once-per-month interval
            interval = apicontractsv1.paymentScheduleTypeInterval()
            interval.length = 1
            interval.unit = apicontractsv1.ARBSubscriptionUnitEnum.months

            # Set infinitely recurring payment schedule
            schedule = apicontractsv1.paymentScheduleType()
            schedule.interval = interval
            schedule.startDate = start_date
            schedule.totalOccurrences = 9999
            schedule.trialOccurrences = 0

            # Set customer payment method
            profile = apicontractsv1.customerProfileIdType()
            profile.customerProfileId = str(customer_profile.pk)
            profile.customerPaymentProfileId = str(payment_profile.pk)
            profile.customerAddressId = str(address_profile.pk)

            # Set Authorizenet subscription contract
            contract = apicontractsv1.ARBSubscriptionType()
            contract.name = name
            contract.amount = self.customer.grand_total
            contract.trialAmount = decimal.Decimal("0.00")
            contract.profile = profile
            contract.paymentSchedule = schedule

            # Create local subscription
            service = AuthorizenetService()
            subscription = Subscription()
            subscription.name = name
            subscription.amount = self.customer.grand_total
            subscription.customer_profile = customer_profile
            subscription.payment_profile = payment_profile
            subscription.address_profile = address_profile

            # Create subscription in Authorizenet and set it to customer
            anet_response = service.create_subscription(subscription, contract)
            subscription.pk = int(anet_response.subscriptionId)
            subscription.save()
            self.customer.subscription = subscription
            self.customer.save(update_fields=["subscription"])
            return HttpResponseRedirect(
                reverse("terminusgps_manager:create subscription success")
            )
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case "E00027":
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! The transaction was unsuccessful. Please try again later."
                            ),
                            code="invalid",
                        ),
                    )
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("Whoops! %(error)s"),
                            code="invalid",
                            params={"error": str(e)},
                        ),
                    )
            return self.form_invalid(form=form)
