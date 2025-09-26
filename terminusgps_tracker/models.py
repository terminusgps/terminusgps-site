import decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.constants import SubscriptionStatus
from terminusgps_payments.models import Subscription

from .managers import UserExclusiveManager


class Customer(models.Model):
    """A Terminus GPS customer."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    subscription = models.ForeignKey(
        "terminusgps_payments.Subscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """Customer subscription."""
    wialon_user_id = models.IntegerField(default=None, null=True, blank=True)
    """Wialon user id."""
    wialon_resource_id = models.IntegerField(
        default=None, null=True, blank=True
    )
    """Wialon resource/account id."""
    tax_rate = models.DecimalField(
        default=0.0825, decimal_places=4, max_digits=5
    )
    """Customer tax rate."""

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        """Returns the customer's email address/username."""
        return self.user.email if self.user.email else self.user.username

    def get_tax_rate_display(self) -> str:
        """Returns the customer's tax rate as a percentage."""
        return f"{self.tax_rate:.2%}"

    def get_units(self) -> models.QuerySet:
        """Returns a queryset of customer wialon units for the customer."""
        return CustomerWialonUnit.objects.for_user(self.user)

    def get_subscription_subtotal(self) -> decimal.Decimal:
        """Returns the subscription subtotal for the customer."""
        unit_qs = self.get_units()
        if unit_qs.count() == 0:
            return decimal.Decimal("0.00")
        prices_aggregate = unit_qs.aggregate(models.Sum("tier__price"))
        return prices_aggregate["tier__price__sum"]

    def get_subscription_grand_total(self) -> decimal.Decimal:
        """Returns the subscription grand total for the customer."""
        subtotal = self.get_subscription_subtotal()
        return round(subtotal * (1 + self.tax_rate), ndigits=2)

    @property
    def is_subscribed(self) -> bool:
        """Whether the customer is subscribed to Terminus GPS."""
        try:
            subscription = Subscription.objects.filter(
                customer_profile__user=self.user
            ).get(name="Terminus GPS Subscription")
            return subscription.status == SubscriptionStatus.ACTIVE
        except Subscription.DoesNotExist:
            return False


class CustomerWialonUnit(models.Model):
    """A customer Wialon unit."""

    wialon_id = models.PositiveIntegerField()
    """Wialon unit id."""
    name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        help_text="Enter a memorable name.",
    )
    """Wialon unit name."""
    imei = models.CharField(
        max_length=16,
        help_text="Enter the IMEI # found on your installed device.",
    )
    """Wialon unit IMEI # (sys_unique_id in Wialon)."""
    tier = models.ForeignKey(
        "terminusgps_tracker.SubscriptionTier",
        on_delete=models.PROTECT,
        related_name="units",
        help_text="Select a tier.",
    )
    """Subscription tier."""
    customer = models.ForeignKey(
        "terminusgps_tracker.Customer",
        on_delete=models.CASCADE,
        related_name="units",
    )
    """Associated customer."""
    objects = UserExclusiveManager()

    class Meta:
        verbose_name = _("wialon unit")
        verbose_name_plural = _("wialon units")

    def __str__(self) -> str:
        """Returns the unit's name or 'Wialon Unit #<pk>'."""
        return self.name if self.name else f"Wialon Unit #{self.pk}"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the unit's detail view."""
        return reverse(
            "terminusgps_tracker:detail unit", kwargs={"unit_pk": self.pk}
        )


class SubscriptionTier(models.Model):
    """A subscription tier."""

    name = models.CharField(max_length=64)
    """Subscription tier name."""
    price = models.DecimalField(max_digits=10, decimal_places=2, default=24.99)
    """Subscription tier price."""

    class Meta:
        verbose_name = _("subscription tier")
        verbose_name_plural = _("subscription tiers")

    def __str__(self) -> str:
        """Returns the subscription tier name."""
        return self.name

    def get_price_display(self) -> str:
        return f"${self.price}"
