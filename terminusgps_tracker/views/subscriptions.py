import decimal
import typing

from authorizenet import apicontractsv1
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from terminusgps.authorizenet.profiles import SubscriptionProfile
from terminusgps.authorizenet.utils import (
    generate_monthly_subscription_schedule,
)
from terminusgps.django.mixins import HtmxTemplateResponseMixin

from terminusgps_tracker.forms import SubscriptionCreationForm
from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    Subscription,
    SubscriptionTier,
)


def calculate_amount_plus_tax(
    amount: decimal.Decimal, tax_rate: decimal.Decimal | None = None
) -> decimal.Decimal:
    if tax_rate is None:
        tax_rate = settings.DEFAULT_TAX_RATE
    return round(amount * (1 + tax_rate), ndigits=2)


class SubscriptionTierListView(HtmxTemplateResponseMixin, ListView):
    content_type = "text/html"
    context_object_name = "tier_list"
    extra_context = {"title": "Subscription Tiers"}
    http_method_names = ["get"]
    model = SubscriptionTier
    order_by = "amount"
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_tier_list.html"
    )
    queryset = SubscriptionTier.objects.exclude(name__icontains="custom")
    template_name = "terminusgps_tracker/subscriptions/tier_list.html"


class SubscriptionTierDetailView(HtmxTemplateResponseMixin, DetailView):
    content_type = "text/html"
    context_object_name = "tier"
    extra_context = {"title": "Subscription Tier Details"}
    http_method_names = ["get"]
    model = SubscriptionTier
    order_by = "amount"
    template_name = "terminusgps_tracker/subscriptions/tier_detail.html"
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_tier_detail.html"
    )


class SubscriptionPricingView(HtmxTemplateResponseMixin, TemplateView):
    content_type = "text/html"
    extra_context = {"title": "Pricing"}
    http_method_names = ["get"]
    template_name = "terminusgps_tracker/subscriptions/pricing.html"
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_pricing.html"
    )


class SubscriptionDetailView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, DetailView
):
    content_type = "text/html"
    context_object_name = "subscription"
    extra_context = {"title": "Subscription Details"}
    http_method_names = ["get", "delete"]
    login_url = reverse_lazy("login")
    model = Subscription
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_detail.html"
    )
    permission_denied_message = "Please login to view this content."
    queryset = Subscription.objects.select_related(
        "payment", "address", "tier"
    )
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/detail.html"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.get_object() or not self.request.headers.get("HX-Request"):
            return HttpResponse(status=403)
        subscription = self.get_object()
        subscription.authorizenet_cancel()
        subscription.delete()
        return super().get(request, *args, **kwargs)

    def get_object(self) -> Subscription | None:
        try:
            return Subscription.objects.get(customer__user=self.request.user)
        except Subscription.DoesNotExist:
            return

    def get_context_data(self, **kwargs) -> dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        subscription = self.get_object()
        if subscription is not None:
            subscription.authorizenet_sync()
            context["paymentProfile"] = (
                subscription.payment.authorizenet_get_profile().paymentProfile
            )
            context["addressProfile"] = (
                subscription.address.authorizenet_get_profile().address
            )
        return context


class SubscriptionUpdateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, UpdateView
):
    content_type = "text/html"
    http_method_names = ["get", "post"]
    extra_context = {"title": "Subscription Update"}
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/update.html"
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_update.html"
    )
    model = Subscription
    queryset = Subscription.objects.select_related("customer")
    fields = ["tier", "payment", "address"]
    success_url = reverse_lazy("tracker:subscription detail")

    def form_valid(
        self, form: forms.ModelForm
    ) -> HttpResponse | HttpResponseRedirect:
        subscription = self.get_object()
        if any(
            [
                subscription.address != form.cleaned_data["address"],
                subscription.payment != form.cleaned_data["payment"],
                subscription.tier != form.cleaned_data["tier"],
            ]
        ):
            subscription.address = form.cleaned_data["address"]
            subscription.payment = form.cleaned_data["payment"]
            subscription.tier = form.cleaned_data["tier"]
            subscription.authorizenet_update()
            subscription.save()
        return super().form_valid(form=form)

    def get_form(self, form_class=None) -> forms.ModelForm:
        form = super().get_form(form_class=form_class)
        tier_qs = SubscriptionTier.objects.exclude(name__icontains="custom")
        address_choices = self.generate_shipping_address_choices()
        payment_choices = self.generate_payment_method_choices()
        form.fields["tier"].queryset = tier_qs
        form.fields["tier"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        form.fields["address"].choices = address_choices
        form.fields["address"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        form.fields["payment"].choices = payment_choices
        form.fields["payment"].widget.attrs.update(
            {"class": settings.DEFAULT_FIELD_CLASS}
        )
        return form

    def get_object(self) -> Subscription:
        return Subscription.objects.get(customer__user=self.request.user)

    def generate_payment_method_choices(self) -> list[tuple[int, str]]:
        choices = []
        if CustomerPaymentMethod.objects.filter(
            customer__user=self.request.user
        ).exists():
            customer_payments = CustomerPaymentMethod.objects.filter(
                customer__user=self.request.user
            )
            for payment in customer_payments:
                card_type = payment.authorizenet_get_profile().paymentProfile.payment.creditCard.cardType
                card_last_4 = int(
                    str(
                        payment.authorizenet_get_profile().paymentProfile.payment.creditCard.cardNumber
                    )[-4:]
                )
                choices.append(
                    (payment.pk, _(f"{card_type} ending in {card_last_4}"))
                )
        return choices

    def generate_shipping_address_choices(self) -> list[tuple[int, str]]:
        choices = []
        if CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        ).exists():
            customer_addresses = CustomerShippingAddress.objects.filter(
                customer__user=self.request.user
            )
            for address in customer_addresses:
                choices.append(
                    (
                        address.pk,
                        _(
                            str(
                                address.authorizenet_get_profile().address.address
                            )
                        ),
                    )
                )
        return choices


class SubscriptionCreateView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, FormView
):
    content_type = "text/html"
    http_method_name = ["get", "post"]
    extra_context = {"title": "Subscription Creation"}
    login_url = reverse_lazy("login")
    permission_denied_message = "Please login to view this content."
    raise_exception = False
    template_name = "terminusgps_tracker/subscriptions/create.html"
    partial_template_name = (
        "terminusgps_tracker/subscriptions/partials/_create.html"
    )
    form_class = SubscriptionCreationForm
    success_url = reverse_lazy("tracker:subscription detail")

    def get_form(self, form_class=None) -> SubscriptionCreationForm:
        form = super().get_form(form_class=form_class)
        tier_qs = SubscriptionTier.objects.exclude(name__icontains="custom")
        address_choices = self.generate_shipping_address_choices()
        payment_choices = self.generate_payment_method_choices()
        form.fields["tier"].queryset = tier_qs
        form.fields["address"].choices = address_choices
        form.fields["payment"].choices = payment_choices
        return form

    def get_initial(self, **kwargs) -> dict[str, typing.Any]:
        initial: dict[str, typing.Any] = super().get_initial(**kwargs)
        initial["tier"] = (
            SubscriptionTier.objects.exclude(name__icontains="custom")
            .order_by("amount")
            .first()
        )
        return initial

    def generate_payment_method_choices(self) -> list[tuple[int, str]]:
        choices = []
        if CustomerPaymentMethod.objects.filter(
            customer__user=self.request.user
        ).exists():
            customer_payments = CustomerPaymentMethod.objects.filter(
                customer__user=self.request.user
            )
            for payment in customer_payments:
                card_type = payment.authorizenet_get_profile().paymentProfile.payment.creditCard.cardType
                card_last_4 = int(
                    str(
                        payment.authorizenet_get_profile().paymentProfile.payment.creditCard.cardNumber
                    )[-4:]
                )
                choices.append(
                    (payment.pk, _(f"{card_type} ending in {card_last_4}"))
                )
        return choices

    def generate_shipping_address_choices(self) -> list[tuple[int, str]]:
        choices = []
        if CustomerShippingAddress.objects.filter(
            customer__user=self.request.user
        ).exists():
            customer_addresses = CustomerShippingAddress.objects.filter(
                customer__user=self.request.user
            )
            for address in customer_addresses:
                choices.append(
                    (
                        address.pk,
                        _(
                            str(
                                address.authorizenet_get_profile().address.address
                            )
                        ),
                    )
                )
        return choices

    @transaction.atomic
    def form_valid(
        self, form: SubscriptionCreationForm
    ) -> HttpResponse | HttpResponseRedirect:
        customer = Customer.objects.get(user=self.request.user)
        address = form.cleaned_data["address"]
        payment = form.cleaned_data["payment"]
        tier = form.cleaned_data["tier"]

        subscription_profile = SubscriptionProfile(
            customer_profile_id=customer.user.pk, id=None
        )
        sub_obj = apicontractsv1.ARBSubscriptionType(
            name=f"{customer}'s {tier} Subscription",
            paymentSchedule=generate_monthly_subscription_schedule(
                timezone.now()
            ),
            amount=str(calculate_amount_plus_tax(tier.amount)),
            trialAmount=str(0.00),
            profile=apicontractsv1.customerProfileIdType(
                customerProfileId=str(customer.authorizenet_profile_id),
                customerPaymentProfileId=str(payment.id),
                customerAddressId=str(address.id),
            ),
        )
        Subscription.objects.create(
            id=subscription_profile.create(sub_obj),
            customer=customer,
            tier=tier,
            address=address,
            payment=payment,
        )
        return super().form_valid(form=form)
