import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import subscriptions


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
    units = models.ManyToManyField(
        "terminusgps_tracker.CustomerWialonUnit", blank=True, default=None
    )
    """Associated customer wialon units."""
    start_date = models.DateTimeField(null=True, blank=True, default=None)
    """Start date/time for the subscription."""

    def __str__(self) -> str:
        """Returns the subscription name."""
        return self.name

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the subscription's detail view."""
        return reverse(
            "tracker:subscription detail",
            kwargs={"customer_pk": self.customer.pk, "sub_pk": self.pk},
        )

    def get_update_url(self) -> str:
        """Returns a URL pointing to the subscription's update view."""
        return reverse(
            "tracker:subscription update",
            kwargs={"customer_pk": self.customer.pk, "sub_pk": self.pk},
        )

    def get_delete_url(self) -> str:
        """Returns a URL pointing to the subscription's delete view."""
        return reverse(
            "tracker:subscription delete",
            kwargs={"customer_pk": self.customer.pk, "sub_pk": self.pk},
        )

    def get_remaining_days(self) -> int:
        """Returns the number of days remaining before the next subscription payment is required."""
        next_payment = self.get_next_payment_date()

        if next_payment == self.start_date:
            return 0
        return (next_payment - timezone.now()).days

    def get_next_payment_date(self) -> datetime.datetime:
        """Returns the next expected payment date for the subscription."""
        if not self.authorizenet_get_transaction_list():
            return self.start_date

        now = timezone.now()
        next = self.start_date.replace(
            month=now.month, year=now.year
        ) + relativedelta(months=1)
        return next if now.day >= next.day else next.replace(month=now.month)

    def authorizenet_get_subscription(
        self, include_transactions: bool = False
    ):
        return subscriptions.get_subscription(
            subscription_id=self.pk, include_transactions=include_transactions
        )

    def authorizenet_get_transaction_list(self) -> list:
        anet_sub = self.authorizenet_get_subscription(
            include_transactions=True
        )
        if anet_sub is None or not hasattr(anet_sub, "arbTransactions"):
            return []
        return [t for t in anet_sub.arbTransactions]

    def _authorizenet_get_remote_payment_id(self) -> int | None:
        anet_sub = self.authorizenet_get_subscription().subscription
        if any(
            [
                anet_sub is None,
                not hasattr(anet_sub, "profile"),
                not hasattr(anet_sub.profile, "paymentProfile"),
            ]
        ):
            return
        return int(anet_sub.profile.paymentProfile.customerPaymentProfileId)

    def _authorizenet_get_remote_address_id(self) -> int | None:
        anet_sub = self.authorizenet_get_subscription().subscription
        if any(
            [
                anet_sub is None,
                not hasattr(anet_sub, "profile"),
                not hasattr(anet_sub.profile, "shippingProfile"),
            ]
        ):
            return
        return int(anet_sub.profile.shippingProfile.customerAddressId)

    def _authorizenet_get_remote_status(self) -> str | None:
        anet_sub = self.authorizenet_get_subscription().subscription
        if anet_sub is None or not hasattr(anet_sub, "status"):
            return
        return str(anet_sub.status)


class SubscriptionTier(models.Model):
    """A subscription tier for a customer unit."""

    name = models.CharField(max_length=64)
    """Subscription tier name."""
    desc = models.TextField(
        max_length=1024, null=True, blank=True, default=None
    )
    """Subscription tier description."""
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=9.99)
    """Subscription tier $ amount."""

    def __str__(self) -> str:
        """Returns the subscription tier name."""
        return self.name

    def get_amount_display(self) -> str:
        """Returns the dollar amount of the subscription tier with a dollar sign."""
        return f"${self.amount}"
