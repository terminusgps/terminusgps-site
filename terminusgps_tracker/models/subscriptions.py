import datetime
import decimal

from authorizenet import apicontractsv1
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.profiles import SubscriptionProfile
from terminusgps.authorizenet.utils import (
    generate_monthly_subscription_schedule,
)

from .customers import CustomerPaymentMethod, CustomerShippingAddress


def calculate_amount_plus_tax(
    amount: decimal.Decimal, tax_rate: decimal.Decimal | None = None
) -> decimal.Decimal:
    if tax_rate is None:
        tax_rate = settings.DEFAULT_TAX_RATE
    return round(amount * (1 + tax_rate), ndigits=2)


class SubscriptionTier(models.Model):
    name = models.CharField(max_length=128)
    """A subscription tier name."""
    desc = models.TextField(max_length=1024)
    """A subscription tier description."""
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=9.99)
    """$ amount (monthly) of the subscription tier."""
    features = models.ManyToManyField(
        "terminusgps_tracker.SubscriptionFeature", related_name="features"
    )
    """Features granted by the subscription."""

    def __str__(self) -> str:
        """Returns the subscription tier name."""
        return self.name

    def get_amount_display(self) -> str:
        """Returns the subscription tier amount as a USD dollar amount. Format: ``"$<AMOUNT>"``."""
        return f"${self.amount:.2d}"


class SubscriptionFeature(models.Model):
    """A customer subscription feature."""

    class SubscriptionFeatureAmount(models.IntegerChoices):
        """An amount of a subscription feature as an integer."""

        MINIMUM = 5, _("5")
        """Minimum amount of a feature."""
        MID = 25, _("25")
        """Medium/moderate amount of a feature."""
        MAXIMUM = 150, _("150")
        """Maximum amount of a feature."""
        INFINITE = 999, _("∞")
        """Infinite amount of a feature."""

    name = models.CharField(max_length=128)
    """Name of the subscription feature."""
    desc = models.TextField(max_length=2048)
    """Description of the subscription feature."""
    amount = models.IntegerField(
        choices=SubscriptionFeatureAmount.choices,
        null=True,
        blank=True,
        default=None,
    )
    """An amount for the subscription feature."""

    def __str__(self) -> str:
        """Returns subscription feature in the format ``"<AMOUNT> <NAME>"``."""
        if self.amount is not None:
            return f"{self.get_amount_display()} {self.name}"
        return self.name


class Subscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        """An active subscription."""
        EXPIRED = "expired", _("Expired")
        """An expired subscription."""
        SUSPENDED = "suspended", _("Suspended")
        """A suspended subscription."""
        CANCELED = "canceled", _("Canceled")
        """A canceled subscription."""
        TERMINATED = "terminated", _("Terminated")
        """A terminated subscription."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet subscription id."""
    start_date = models.DateField(auto_now_add=True)
    """Start date for the subscription."""
    tier = models.ForeignKey(
        "terminusgps_tracker.SubscriptionTier",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )
    """Current subscription tier."""
    status = models.CharField(
        max_length=64,
        choices=SubscriptionStatus.choices,
        default=None,
        blank=True,
        null=True,
    )
    customer = models.OneToOneField(
        "terminusgps_tracker.Customer", on_delete=models.CASCADE
    )
    """Associated customer."""
    payment = models.OneToOneField(
        "terminusgps_tracker.CustomerPaymentMethod", on_delete=models.CASCADE
    )
    """Associated payment method."""
    address = models.OneToOneField(
        "terminusgps_tracker.CustomerShippingAddress", on_delete=models.CASCADE
    )
    """Associated payment method."""

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def __str__(self) -> str:
        return (
            f"{self.customer}'s {self.tier} Subscription"
            if self.tier is not None
            else f"{self.customer}'s Subscription"
        )

    def save(self, **kwargs) -> None:
        self.full_clean()
        super().save(**kwargs)

    def authorizenet_get_profile(self) -> SubscriptionProfile:
        """Returns the Authorizenet subscription profile for the subscription."""
        return SubscriptionProfile(
            customer_profile_id=str(self.customer.authorizenet_profile_id),
            id=str(self.pk),
        )

    @transaction.atomic
    def authorizenet_sync(self) -> None:
        """Syncs the subscription's status, payment method and shipping address with Authorizenet."""
        self.authorizenet_sync_status()
        self.authorizenet_sync_payment()
        self.authorizenet_sync_address()

    @transaction.atomic
    def authorizenet_sync_status(self) -> None:
        """Syncs the subscription's status with Authorizenet."""
        current_status = self.authorizenet_get_profile().status
        if current_status is not None:
            self.status = current_status

    @transaction.atomic
    def authorizenet_sync_payment(self) -> None:
        """Syncs the subscription's payment method with Authorizenet."""
        current_payment_id = self.authorizenet_get_profile().payment_id
        if current_payment_id is not None:
            self.payment, _ = CustomerPaymentMethod.objects.filter(
                customer=self.customer
            ).get_or_create(pk=current_payment_id, customer=self.customer)

    @transaction.atomic
    def authorizenet_sync_address(self) -> None:
        """Syncs the subscription's shipping address with Authorizenet."""
        current_address_id = self.authorizenet_get_profile().address_id
        if current_address_id is not None:
            self.address, _ = CustomerShippingAddress.objects.filter(
                customer=self.customer
            ).get_or_create(pk=current_address_id, customer=self.customer)

    @transaction.atomic
    def authorizenet_cancel(self) -> None:
        """Cancels the subscription with Authorizenet."""
        self.authorizenet_get_profile().delete()
        self.status = self.SubscriptionStatus.CANCELED

    @transaction.atomic
    def authorizenet_update(self) -> None:
        """Updates the subscription with Authorizenet."""
        self.authorizenet_get_profile().update(
            self.generate_subscription_obj()
        )

    def authorizenet_get_transactions(self) -> list[dict[str, str]]:
        """Returns a list of subscription transactions from Authorizenet."""
        return self.authorizenet_get_profile().transactions

    def get_subscription_name(self) -> str:
        """Returns a subscription name in the format: <TIER> Subscription"""
        return f"{self.tier} Subscription"

    def generate_subscription_obj(
        self,
        start_date: datetime.date | None = None,
        total_occurrences: int = 9999,
        trial_occurrences: int = 0,
    ) -> apicontractsv1.ARBSubscriptionType:
        """
        Generates and returns a subscription object for Authorizenet API calls.

        If ``start_date`` is provided, adds a monthly payment schedule to the subscription starting on that date.

        :param start_date: A start date for the subscription. Default is :py:obj:`None`
        :type start_date: :py:obj:`~datetime.date` | :py:obj:`None`
        :param total_occurrences: Total occurrences for the subscription interval. Default is :py:obj:`9999`.
        :type total_occurrences: :py:obj:`int`
        :param trial_occurrences: Trial occurrences for the subscription interval. Default is :py:obj:`0`.
        :type trial_occurrences: :py:obj:`int`
        :returns: A subscription object for Authorizenet API calls.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType`

        """
        sub_obj = apicontractsv1.ARBSubscriptionType(
            name=self.get_subscription_name(),
            amount=str(calculate_amount_plus_tax(self.tier.amount)),
            trialAmount=str(0.00),
            profile=apicontractsv1.customerProfileIdType(
                customerProfileId=str(self.customer.authorizenet_profile_id),
                customerPaymentProfileId=str(self.payment.id),
                customerAddressId=str(self.address.id),
            ),
        )
        if start_date:
            sub_obj.paymentSchedule = generate_monthly_subscription_schedule(
                start_date, total_occurrences, trial_occurrences
            )
        return sub_obj

    def clean(self):
        super().clean()
        if (
            self.payment
            and hasattr(self, "customer")
            and self.customer
            and self.payment.customer != self.customer
        ):
            raise ValidationError(
                {
                    "payment": _(
                        "Payment method must belong to the same customer as the subscription."
                    )
                }
            )
        if (
            self.address
            and hasattr(self, "customer")
            and self.customer
            and self.address.customer != self.customer
        ):
            raise ValidationError(
                {
                    "address": _(
                        "Shipping address must belong to the same customer as the subscription."
                    )
                }
            )
