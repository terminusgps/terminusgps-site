from authorizenet import apicontractsv1
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        CANCELED = "canceled", _("Canceled")
        EXPIRED = "expired", _("Expired")
        SUSPENDED = "suspended", _("Suspended")
        TERMINATED = "terminated", _("Terminated")

    class SubscriptionLength(models.IntegerChoices):
        HALF_YEAR = 6, _("Half-year")
        FULL_YEAR = 12, _("Full-year")

    customer = models.OneToOneField(
        "terminusgps_tracker.Customer",
        on_delete=models.PROTECT,
        related_name="subscription",
    )
    """A customer."""
    authorizenet_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    """An Authorizenet subscription id."""
    length = models.IntegerField(
        choices=SubscriptionLength.choices, default=SubscriptionLength.FULL_YEAR
    )
    """Length of the subscription (in months)."""
    tier = models.ForeignKey(
        "terminusgps_tracker.SubscriptionTier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="tier",
    )
    """Current subscription tier."""
    payment = models.ForeignKey(
        "terminusgps_tracker.CustomerPaymentMethod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="payment",
    )
    """A payment method."""
    address = models.ForeignKey(
        "terminusgps_tracker.CustomerShippingAddress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="address",
    )
    """A shipping address."""
    status = models.CharField(
        max_length=16,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.SUSPENDED,
    )
    """Current Authorizenet subscription status."""

    def __str__(self) -> str:
        return f"{self.customer}'s Subscription"

    def create_payment_schedule(self) -> apicontractsv1.paymentScheduleType:
        return apicontractsv1.paymentScheduleType(
            interval=apicontractsv1.paymentScheduleTypeInterval(
                length=self.length, unit=apicontractsv1.ARBSubscriptionUnitEnum.months
            ),
            startDate=timezone.now(),
            totalOccurrences=1,
            trialOccurrences=0,
        )


class SubscriptionTier(models.Model):
    name = models.CharField(max_length=128)
    """A subscription tier name."""
    desc = models.CharField(max_length=1024)
    """A subscription tier description."""
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=9.99)
    """$ amount (monthly) of the subscription tier."""
    features = models.ManyToManyField(
        "terminusgps_tracker.SubscriptionFeature", related_name="features"
    )
    """Features granted by the subscription."""

    def __str__(self) -> str:
        return self.name

    def get_amount_display(self) -> str:
        return f"${self.amount:.2d}"


class SubscriptionFeature(models.Model):
    class SubscriptionFeatureAmount(models.IntegerChoices):
        MINIMUM = 5, _("5")
        MID = 25, _("25")
        MAXIMUM = 150, _("150")
        INFINITE = 999, _("∞")

    name = models.CharField(max_length=128)
    """Name of the feature."""
    desc = models.CharField(max_length=2048)
    """Description of the feature."""
    amount = models.IntegerField(
        choices=SubscriptionFeatureAmount.choices, null=True, blank=True, default=None
    )
    """An amount for the feature."""

    def __str__(self) -> str:
        if self.amount is None:
            return self.name
        return f"{self.get_amount_display()} {self.name}"
