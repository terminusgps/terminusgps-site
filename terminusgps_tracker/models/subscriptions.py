import decimal

from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.profiles import SubscriptionProfile
from terminusgps.authorizenet.utils import calculate_amount_plus_tax

from terminusgps_tracker.models import (
    CustomerPaymentMethod,
    CustomerShippingAddress,
)


class Subscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
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
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.SUSPENDED,
    )
    """Authorizenet subscription status."""
    customer = models.OneToOneField(
        "terminusgps_tracker.Customer", on_delete=models.CASCADE
    )
    """Associated customer."""
    payment = models.OneToOneField(
        "terminusgps_tracker.CustomerPaymentMethod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """Associated payment method."""
    address = models.OneToOneField(
        "terminusgps_tracker.CustomerShippingAddress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """Associated shipping address."""
    features = models.ManyToManyField(
        "terminusgps_tracker.SubscriptionFeature", blank=True, default=None
    )
    """Associated subscription features."""
    units = models.ManyToManyField(
        "terminusgps_tracker.CustomerWialonUnit", blank=True, default=None
    )
    """Associated customer wialon units."""

    def __str__(self) -> str:
        """Returns the subscription name."""
        return self.name

    def save(self, **kwargs) -> None:
        """Checks if the subscription is out of sync with Authorizenet and syncs data if necessary."""
        if self.authorizenet_needs_sync():
            self.authorizenet_sync()
        super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the subscription's detail view."""
        return reverse(
            "tracker:subscription detail", kwargs={"sub_pk": self.pk}
        )

    def get_update_url(self) -> str:
        """Returns a URL pointing to the subscription's update view."""
        return reverse(
            "tracker:subscription update", kwargs={"sub_pk": self.pk}
        )

    def get_delete_url(self) -> str:
        """Returns a URL pointing to the subscription's delete view."""
        return reverse(
            "tracker:subscription delete", kwargs={"sub_pk": self.pk}
        )

    def calculate_amount(self, add_tax: bool = True) -> decimal.Decimal:
        amount_list = []

        if self.units.exists():
            amount_list.extend(
                self.units.values_list("tier__amount", flat=True)
            )
        if self.features.exists():
            amount_list.extend(
                [f.calculate_amount() for f in self.features.all()]
            )

        final_amount = decimal.Decimal(sum(amount_list))
        return (
            calculate_amount_plus_tax(final_amount)
            if add_tax
            else final_amount
        )

    def authorizenet_sync(self) -> None:
        """Syncs the subscription payment, address and status with Authorizenet."""
        sprofile = self.authorizenet_get_subscription_profile()
        self.authorizenet_sync_status(sprofile)
        self.authorizenet_sync_payment(sprofile)
        self.authorizenet_sync_address(sprofile)

    @transaction.atomic
    def authorizenet_sync_payment(
        self, sprofile: SubscriptionProfile
    ) -> SubscriptionProfile:
        """Creates/retrieves and sets the payment for the subscription from Authorizenet."""
        self.payment, _ = CustomerPaymentMethod.objects.get_or_create(
            id=sprofile.address_id, customer=self.customer
        )
        return sprofile

    @transaction.atomic
    def authorizenet_sync_address(
        self, sprofile: SubscriptionProfile
    ) -> SubscriptionProfile:
        """Creates/retrieves and sets the address for the subscription from Authorizenet."""
        self.address, _ = CustomerShippingAddress.objects.get_or_create(
            id=sprofile.address_id, customer=self.customer
        )
        return sprofile

    @transaction.atomic
    def authorizenet_sync_status(
        self, sprofile: SubscriptionProfile
    ) -> SubscriptionProfile:
        """Retrieves and sets the status for the subscription from Authorizenet."""
        self.status = sprofile.status
        return sprofile

    def authorizenet_needs_sync(self) -> bool:
        """Returns :py:obj:`True` if the subscription is missing a payment or address."""
        return not bool(self.payment or self.address)

    def authorizenet_get_subscription_profile(self) -> SubscriptionProfile:
        """Returns a :py:obj:`~terminusgps.authorizenet.profiles.subscriptions.SubscriptionProfile` for the subscription."""
        return SubscriptionProfile(
            customer_profile_id=self.customer.authorizenet_profile_id,
            id=self.pk,
        )


class SubscriptionFeature(models.Model):
    """A subscription feature for a customer subscription."""

    name = models.CharField(max_length=64)
    """Subscription feature name."""
    desc = models.TextField(max_length=1024)
    """Subscription feature description."""
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=9.99)
    """Subscription feature $ amount."""
    total = models.PositiveIntegerField(default=1)
    """Subscription feature total."""

    def __str__(self) -> str:
        """Returns the subscription feature name."""
        if self.total != 1:
            return f"{self.total}x {self.name}"
        return self.name

    def get_amount_display(self) -> str:
        return f"${self.amount}"

    def calculate_amount(self) -> decimal.Decimal:
        return self.amount * self.total


class SubscriptionTier(models.Model):
    """A subscription tier for a customer unit."""

    name = models.CharField(max_length=64)
    """Subscription tier name."""
    desc = models.TextField(max_length=1024)
    """Subscription tier description."""
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=9.99)
    """Subscription tier $ amount."""

    def __str__(self) -> str:
        """Returns the subscription tier name."""
        return self.name

    def get_amount_display(self) -> str:
        return f"${self.amount}"
