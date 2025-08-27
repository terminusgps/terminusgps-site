import decimal
import typing

from authorizenet import apicontractsv1
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, FormView
from terminusgps.authorizenet import subscriptions as anet_subscriptions
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import CustomerSubscriptionUpdateForm
from terminusgps_tracker.models import Customer, CustomerSubscription
from terminusgps_tracker.views.mixins import (
    CustomerAuthenticationRequiredMixin,
)


class CustomerSubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, CreateView
):
    content_type = "text/html"
    fields = ["payment", "address"]
    http_method_names = ["get", "post"]
    model = CustomerSubscription
    login_url = reverse_lazy("login")
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_create.html"
    )
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/create.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["payment"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        form.fields["payment"].label = "Payment Method"
        form.fields["address"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        form.fields["address"].label = "Shipping Address"
        return form

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        customer = Customer.objects.get(user=self.request.user)
        initial["payment"] = customer.payments.first()
        initial["address"] = customer.addresses.first()
        return initial

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        customer = Customer.objects.get(user=self.request.user)
        subscription = CustomerSubscription(customer=customer)
        context["customer"] = customer
        if customer.units.count() != 0:
            context["sub_total"] = subscription.get_subtotal()
            context["grand_total"] = subscription.get_grand_total()
        else:
            context["sub_total"] = None
            context["grand_total"] = None
        return context

    def get_success_url(
        self, subscription: CustomerSubscription | None = None
    ) -> str:
        if not subscription:
            return reverse("tracker:subscription")
        return reverse(
            "tracker:detail subscription",
            kwargs={
                "customer_pk": subscription.customer.pk,
                "subscription_pk": subscription.pk,
            },
        )

    def form_valid(self, form: forms.ModelForm) -> HttpResponse:
        customer = Customer.objects.get(user=self.request.user)
        if customer.units.count() == 0:
            form.add_error(
                None,
                ValidationError(
                    _(
                        "Whoops! You can't subscribe until you register a unit."
                    ),
                    code="invalid",
                ),
            )
            return self.form_invalid(form=form)
        try:
            customer_profile_id = customer.authorizenet_profile_id
            payment_profile_id = form.cleaned_data["payment"].pk
            address_profile_id = form.cleaned_data["address"].pk
            subscription = CustomerSubscription(
                customer=customer,
                address=form.cleaned_data["address"],
                payment=form.cleaned_data["payment"],
            )

            response = anet_subscriptions.create_subscription(
                subscription_obj=apicontractsv1.ARBSubscriptionType(
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
                    amount=subscription.get_grand_total(),
                    trialAmount=decimal.Decimal("0.00"),
                    profile=apicontractsv1.customerProfileIdType(
                        customerProfileId=customer_profile_id,
                        customerPaymentProfileId=payment_profile_id,
                        customerAddressId=address_profile_id,
                    ),
                )
            )
            subscription.pk = int(response.subscriptionId)
            subscription.save()
            return HttpResponseRedirect(self.get_success_url(subscription))
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _("%(code)s: '%(message)s'"),
                            code="invalid",
                            params={"code": e.code, "message": e.message},
                        ),
                    )
            return self.form_invalid(form=form)


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

    def get_queryset(
        self,
    ) -> QuerySet[CustomerSubscription, CustomerSubscription]:
        return CustomerSubscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("address", "customer", "payment")

    def get_success_url(self) -> str:
        return reverse(
            "tracker:detail subscription",
            kwargs={
                "customer_pk": self.kwargs["customer_pk"],
                "subscription_pk": self.kwargs["subscription_pk"],
            },
        )

    def form_valid(self, form: CustomerSubscriptionUpdateForm) -> HttpResponse:
        try:
            customer = Customer.objects.get(pk=self.kwargs["customer_pk"])
            payment = form.cleaned_data["payment"]
            address = form.cleaned_data["address"]
            anet_subscriptions.update_subscription(
                subscription_id=int(self.kwargs["subscription_pk"]),
                subscription_obj=apicontractsv1.ARBSubscriptionType(
                    profile=apicontractsv1.customerProfileIdType(
                        customerProfileId=str(
                            customer.authorizenet_profile_id
                        ),
                        customerPaymentProfileId=str(payment.pk),
                        customerAddressId=str(address.pk),
                    )
                ),
            )
            return HttpResponseRedirect(self.get_success_url())
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! Something went wrong, please try again later."
                            )
                        ),
                    )
            return self.form_invalid(form=form)


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
        subscription: CustomerSubscription = kwargs["object"]
        context["profile"] = anet_subscriptions.get_subscription(
            subscription_id=subscription.pk, include_transactions=True
        )
        return context

    def get_queryset(
        self,
    ) -> QuerySet[CustomerSubscription, CustomerSubscription]:
        return CustomerSubscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("address", "customer", "payment")


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

    def get_queryset(
        self,
    ) -> QuerySet[CustomerSubscription, CustomerSubscription]:
        return CustomerSubscription.objects.filter(
            customer__pk=self.kwargs["customer_pk"]
        ).select_related("address", "customer", "payment")

    def form_valid(self, form: forms.Form) -> HttpResponse:
        try:
            anet_subscriptions.cancel_subscription(
                subscription_id=self.get_object().pk
            )
            return super().form_valid(form=form)
        except AuthorizenetControllerExecutionError as e:
            match e.code:
                case _:
                    form.add_error(
                        None,
                        ValidationError(
                            _(
                                "Whoops! Something went wrong, please try again later."
                            )
                        ),
                    )
            return self.form_invalid(form=form)

    def get_success_url(self) -> str:
        return reverse(
            "tracker:account",
            kwargs={"customer_pk": self.kwargs["customer_pk"]},
        )
