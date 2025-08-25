import datetime
import decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import profiles as anet_profiles
from terminusgps.authorizenet import subscriptions as anet_subscriptions
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

    def get_authorizenet_profile(self, include_issuer_info: bool = False):
        """Returns the Authorizenet customer profile for the customer."""
        assert self.authorizenet_profile_id is not None, (
            "Customer authorizenet profile id wasn't set."
        )
        return anet_profiles.get_customer_profile(
            customer_profile_id=self.authorizenet_profile_id,
            include_issuer_info=include_issuer_info,
        )

    def get_unit_price_sum(self) -> decimal.Decimal:
        """Returns the sum of all customer unit subscription tiers as a :py:obj:`~decimal.Decimal`."""
        aggregate = (
            CustomerWialonUnit.objects.filter(customer=self)
            .select_related("tier")
            .aggregate(models.Sum("tier__price"))
        )
        return round(aggregate["tier__price__sum"], ndigits=2)

    @property
    def is_subscribed(self) -> bool:
        """Whether or not the customer is subscribed."""
        try:
            active = CustomerSubscription.CustomerSubscriptionStatus.ACTIVE
            status = CustomerSubscription.objects.get(customer=self).status
            return status == active
        except CustomerSubscription.DoesNotExist:
            return False


class CustomerWialonUnit(models.Model):
    """A Wialon unit for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon unit id."""
    name = models.CharField(max_length=64, null=True, blank=True, default=None)
    """Wialon unit name."""
    tier = models.ForeignKey(
        "terminusgps_tracker.CustomerSubscriptionTier",
        on_delete=models.RESTRICT,
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
        """Returns the unit's name or 'Wialon Unit #<pk>'."""
        return self.name if self.name else f"Wialon Unit #{self.pk}"

    def get_wialon_unit(self, session: WialonSession) -> WialonUnit:
        """Returns the customer Wialon unit as an instance of :py:obj:`~terminusgps.wialon.items.unit.WialonUnit`."""
        factory = WialonObjectFactory(session)
        return factory.get("avl_unit", self.pk)


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
        """Returns 'Payment Method #<pk>'."""
        return f"Payment Method #{self.pk}"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the payment method's detail view."""
        return reverse(
            "tracker:detail payment",
            kwargs={"customer_pk": self.customer.pk, "payment_pk": self.pk},
        )

    def get_delete_url(self) -> str:
        """Returns a URL pointing to the payment method's delete view."""
        return reverse(
            "tracker:delete payment",
            kwargs={"customer_pk": self.customer.pk, "payment_pk": self.pk},
        )

    def get_list_url(self) -> str:
        """Returns a URL pointing to the payment method's list view."""
        return reverse(
            "tracker:list payment", kwargs={"customer_pk": self.customer.pk}
        )

    def get_authorizenet_profile(self, include_issuer_info: bool = False):
        """Returns the Authorizenet payment profile for the payment method."""
        assert self.customer.authorizenet_profile_id is not None, (
            "Customer authorizenet profile id wasn't set."
        )
        return anet_profiles.get_customer_payment_profile(
            customer_profile_id=self.customer.authorizenet_profile_id,
            customer_payment_profile_id=self.pk,
            include_issuer_info=include_issuer_info,
        )


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
        """Returns 'Shipping Address #<pk>'."""
        return f"Shipping Address #{self.pk}"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the shipping address' detail view."""
        return reverse(
            "tracker:detail address",
            kwargs={"customer_pk": self.customer.pk, "address_pk": self.pk},
        )

    def get_delete_url(self) -> str:
        """Returns a URL pointing to the shipping address' delete view."""
        return reverse(
            "tracker:delete address",
            kwargs={"customer_pk": self.customer.pk, "address_pk": self.pk},
        )

    def get_list_url(self) -> str:
        """Returns a URL pointing to the shipping address' list view."""
        return reverse(
            "tracker:list address", kwargs={"customer_pk": self.customer.pk}
        )

    def get_authorizenet_profile(self):
        """Returns the Authorizenet address profile for the shipping address."""
        assert self.customer.authorizenet_profile_id, (
            "Customer authorizenet profile id wasn't set."
        )
        return anet_profiles.get_customer_shipping_address(
            customer_profile_id=self.customer.authorizenet_profile_id,
            customer_address_profile_id=self.pk,
        )


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
        "terminusgps_tracker.Customer", on_delete=models.RESTRICT
    )
    """Associated customer."""
    payment = models.OneToOneField(
        "terminusgps_tracker.CustomerPaymentMethod", on_delete=models.RESTRICT
    )
    """Associated payment method."""
    address = models.OneToOneField(
        "terminusgps_tracker.CustomerShippingAddress",
        on_delete=models.RESTRICT,
    )
    """Associated shipping address."""
    start_date = models.DateTimeField(null=True, blank=True, default=None)
    """Start date/time for the subscription."""

    def __str__(self) -> str:
        """Returns the subscription name."""
        return self.name

    def get_authorizenet_profile(self, include_transactions: bool = False):
        return anet_subscriptions.get_subscription(
            subscription_id=self.pk, include_transactions=include_transactions
        )

    def get_authorizenet_status(self) -> str | None:
        """Returns the current subscription status from the Authorizenet API."""
        response = anet_subscriptions.get_subscription_status(
            subscription_id=self.pk
        )
        if response is not None and hasattr(response, "status"):
            return str(response.status)

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

    @transaction.atomic
    def refresh_status(self) -> None:
        """Sets the subscription status to the status returned by the Authorizenet API."""
        if new_status := self.get_authorizenet_status():
            self.status = new_status


class CustomerSubscriptionTier(models.Model):
    """A subscription tier for a customer unit."""

    name = models.CharField(max_length=64)
    """Subscription tier name."""
    price = models.DecimalField(max_digits=9, decimal_places=2, default=24.99)
    """Subscription tier dollar amount."""

    def __str__(self) -> str:
        """Returns the subscription tier name."""
        return self.name

    def get_price_display(self) -> str:
        """Returns the dollar amount of the subscription tier with a dollar sign."""
        return f"${self.price}"
