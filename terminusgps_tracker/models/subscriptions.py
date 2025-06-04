import typing

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.profiles import SubscriptionProfile


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
    tier = models.OneToOneField(
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
        return f"{self.customer}'s Subscription"

    def save(self, **kwargs) -> None:
        self.full_clean()
        super().save(**kwargs)

    @transaction.atomic
    def authorizenet_cancel(self) -> None:
        subscription_profile = SubscriptionProfile(
            customer_profile_id=self.customer.user.pk, id=self.pk
        )
        subscription_profile.cancel()
        self.status = self.SubscriptionStatus.CANCELED

    def authorizenet_get_transactions(self) -> list[dict[str, typing.Any]]:
        subscription_profile = SubscriptionProfile(
            customer_profile_id=self.customer.user.pk, id=self.pk
        )
        return subscription_profile.transactions

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
