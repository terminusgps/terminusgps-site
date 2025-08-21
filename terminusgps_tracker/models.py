import datetime
import decimal
from typing import Literal

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.items import WialonObjectFactory
from terminusgps.wialon.items.unit import WialonUnit
from terminusgps.wialon.session import WialonSession


class Customer(models.Model):
    """A human user."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    authorizenet_profile_id = models.IntegerField(
        default=None, null=True, blank=True
    )
    """Authorizenet customer profile id."""
    wialon_user_id = models.IntegerField(default=None, null=True, blank=True)
    """Wialon user id."""
    wialon_resource_id = models.IntegerField(
        default=None, null=True, blank=True
    )
    """Wialon resource/account id."""

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        """Returns the customer's email address/username."""
        return self.user.email if self.user.email else self.user.username

    def calculate_subscription_amount(
        self, tax_rate: decimal.Decimal | None = None
    ) -> decimal.Decimal:
        unit_qs = CustomerWialonUnit.objects.filter(
            customer=self
        ).prefetch_related("tier")
        sum = decimal.Decimal(
            unit_qs.aggregate(
                models.Sum("tier__amount"), default=decimal.Decimal("24.99")
            )
        )
        return (
            decimal.Decimal(sum * (1 + tax_rate))
            if tax_rate is not None
            else decimal.Decimal(sum)
        )


class CustomerWialonUnit(models.Model):
    """A Wialon unit for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon unit id."""
    name = models.CharField(max_length=64, null=True, blank=True, default=None)
    """Wialon unit name."""

    tier = models.ForeignKey(
        "terminusgps_tracker.SubscriptionTier", on_delete=models.PROTECT
    )
    """Subscription tier for the unit."""
    customer = models.ForeignKey(
        "terminusgps_tracker.Customer",
        on_delete=models.CASCADE,
        related_name="units",
    )
    """Associated customer."""

    class Meta:
        verbose_name = _("customer wialon unit")
        verbose_name_plural = _("customer wialon units")

    def __str__(self) -> str:
        return self.name if self.name else f"Wialon Unit #{self.pk}"

    @property
    def wialon_type(self) -> Literal["avl_unit"]:
        """Returns 'avl_unit'."""
        return "avl_unit"

    def get_wialon_unit(self, session: WialonSession) -> WialonUnit:
        """Returns the customer Wialon unit as an instance of :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`."""
        factory = WialonObjectFactory(session)
        return factory.get(self.wialon_type, self.pk)


class CustomerPaymentMethod(models.Model):
    """A payment method for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet customer payment profile id."""
    customer = models.ForeignKey(
        "terminusgps_tracker.Customer",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    """Associated customer."""

    class Meta:
        verbose_name = _("customer payment method")
        verbose_name_plural = _("customer payment methods")

    def __str__(self) -> str:
        return f"Payment Method #{self.pk}"


class CustomerShippingAddress(models.Model):
    """A shipping address for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet customer shipping profile id."""
    customer = models.ForeignKey(
        "terminusgps_tracker.Customer",
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    """Associated customer."""

    class Meta:
        verbose_name = _("customer shipping address")
        verbose_name_plural = _("customer shipping addresses")

    def __str__(self) -> str:
        return f"Shipping Address #{self.pk}"


class CustomerSubscription(models.Model):
    class CustomerSubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        """Subscription is active in Authorizenet."""
        CANCELED = "canceled", _("Canceled")
        """Subscription was canceled in Authorizenet."""
        EXPIRED = "expired", _("Expired")
        """Subscription was expired in Authorizenet."""
        SUSPENDED = "suspended", _("Suspended")
        """Subscription was suspended in Authorizenet."""
        TERMINATED = "terminated", _("Terminated")
        """Subscription was terminated in Authorizenet."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet subscription id."""
    name = models.CharField(max_length=31)
    """Authorizenet subscription name."""
    status = models.CharField(
        max_length=16,
        choices=CustomerSubscriptionStatus.choices,
        default=CustomerSubscriptionStatus.SUSPENDED,
    )
    """Authorizenet subscription status."""
    customer = models.OneToOneField(
        "terminusgps_tracker.Customer", on_delete=models.PROTECT
    )
    """Associated customer."""
    payment = models.OneToOneField(
        "terminusgps_tracker.CustomerPaymentMethod", on_delete=models.PROTECT
    )
    """Associated payment method."""
    address = models.OneToOneField(
        "terminusgps_tracker.CustomerShippingAddress", on_delete=models.PROTECT
    )
    """Associated shipping address."""
    start_date = models.DateTimeField(null=True, blank=True, default=None)
    """Start date/time for the subscription."""

    def __str__(self) -> str:
        """Returns the subscription name."""
        return self.name

    def get_next_payment_date(self) -> datetime.datetime:
        """Returns the next expected payment date for the subscription."""
        now = timezone.now()
        if not self.start_date:
            return now

        next = self.start_date.replace(
            month=now.month, year=now.year
        ) + relativedelta(months=1)
        return next if now.day >= next.day else next.replace(month=now.month)

    def get_remaining_days(self) -> int:
        """Returns the number of days remaining before the next subscription payment is required."""
        next_payment = self.get_next_payment_date()
        return (next_payment - timezone.now()).days


class CustomerSubscriptionTier(models.Model):
    """A subscription tier for a customer unit."""

    name = models.CharField(max_length=64)
    """Subscription tier name."""
    desc = models.TextField(
        max_length=1024, null=True, blank=True, default=None
    )
    """Subscription tier description."""
    price = models.DecimalField(max_digits=9, decimal_places=2, default=9.99)
    """Subscription tier dollar amount."""

    def __str__(self) -> str:
        """Returns the subscription tier name."""
        return self.name

    def get_price_display(self) -> str:
        """Returns the dollar amount of the subscription tier with a dollar sign."""
        return f"${self.price}"
