import datetime
import decimal

from authorizenet import apicontractsv1
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
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
    desc = models.TextField(max_length=2048)
    """Description of the feature."""
    amount = models.IntegerField(
        choices=SubscriptionFeatureAmount.choices, null=True, blank=True, default=None
    )
    """An amount for the feature."""

    def __str__(self) -> str:
        if not self.amount:
            return self.name
        return f"{self.get_amount_display()} {self.name}"


class CustomerSubscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        CANCELED = "canceled", _("Canceled")
        UNBOUND = "unbound", _("Unbound")
        EXPIRED = "expired", _("Expired")
        SUSPENDED = "suspended", _("Suspended")
        TERMINATED = "terminated", _("Terminated")

    customer = models.OneToOneField(
        "terminusgps_tracker.Customer",
        on_delete=models.PROTECT,
        related_name="subscription",
    )
    """A customer."""
    authorizenet_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    """An Authorizenet subscription id."""
    total_months = models.PositiveIntegerField(
        choices=[(12, _("1 year")), (24, _("2 years"))], default=12
    )
    """Total number of months for the subscription."""
    trial_months = models.PositiveIntegerField(
        choices=[(0, _("0 months")), (1, _("1 month"))], default=0
    )
    """Total number of trial months for the subscription."""
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
        default=SubscriptionStatus.UNBOUND,
    )
    """Current Authorizenet subscription status."""
    _prev_address = models.ForeignKey(
        "terminusgps_tracker.CustomerShippingAddress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="prev_address",
    )
    _prev_payment = models.ForeignKey(
        "terminusgps_tracker.CustomerPaymentMethod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="prev_payment",
    )
    _prev_tier = models.ForeignKey(
        "terminusgps_tracker.SubscriptionTier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name="prev_tier",
    )

    def __str__(self) -> str:
        return f"{self.customer}'s Subscription"

    def save(self, **kwargs) -> None:
        if self.authorizenet_id:
            self.authorizenet_refresh_status()
            self.authorizenet_update_subscription()
        if all([not self.authorizenet_id, self.tier, self.address, self.payment]):
            self.authorizenet_id = self.authorizenet_create_subscription()
        self._prev_tier = self.tier
        self._prev_address = self.address
        self._prev_payment = self.payment
        super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the subscription's detail view."""
        return reverse("detail subscription", kwargs={"pk": self.pk})

    def get_amount_plus_tax(self) -> decimal.Decimal:
        """Returns the amount + tax for the subscription."""
        return round(
            self.tier.amount + (self.tier.amount * settings.DEFAULT_TAX_RATE), ndigits=2
        )

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        if self.authorizenet_id and self.status != self.SubscriptionStatus.CANCELED:
            self.authorizenet_cancel_subscription()
        return super().delete(*args, **kwargs)

    def clean(self) -> None:
        if self.address and self.address.customer.pk != self.customer.pk:
            raise ValidationError(
                {
                    "address": f"Only {self.customer}'s addresses can be assigned to this subscription."
                }
            )
        if self.payment and self.payment.customer.pk != self.customer.pk:
            raise ValidationError(
                {
                    "payment": f"Only {self.customer}'s payments can be assigned to this subscription."
                }
            )

    def authorizenet_update_subscription(self) -> None:
        """
        Updates the subscription in Authorizenet.

        :raises AssertionError: If :py:attr:`authorizenet_id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.authorizenet_id, "Authorizenet id was not set"
        subscription_profile: SubscriptionProfile = (
            self.authorizenet_get_subscription_profile()
        )
        params = apicontractsv1.ARBSubscriptionType()
        cprofile = apicontractsv1.customerProfileIdType()
        updated = []
        if self._prev_tier != self.tier:
            params.name = f"{self.customer}'s {self.tier.name} Subscription"
            params.amount = self.get_amount_plus_tax()
            updated.append(self.tier)
        if self._prev_address != self.address:
            cprofile.customerAddressId = self.address.authorizenet_id
            params.profile = cprofile
            updated.append(self.address)
        if self._prev_payment != self.payment:
            cprofile.customerPaymentProfileId = self.payment.authorizenet_id
            params.profile = cprofile
            updated.append(self.payment)
        if updated:
            subscription_profile.update(params)

    def authorizenet_cancel_subscription(self) -> None:
        """
        Cancels a subscription in Authorizenet.

        :raises AssertionError: If :py:attr:`authorizenet_id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.authorizenet_id, "Authorizenet id was not set"
        self.authorizenet_get_subscription_profile().cancel()

    @transaction.atomic
    def authorizenet_refresh_status(self) -> None:
        """
        Refreshes the subscription status from Authorizenet.

        :raises AssertionError: If :py:attr:`authorizenet_id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.authorizenet_id, "Authorizenet id was not set"
        new_status: str | None = self.authorizenet_get_subscription_profile().status
        if new_status is not None:
            self.status = new_status

    def authorizenet_create_subscription(self) -> int:
        """
        Creates a subscription in Authorizenet.

        :raises AssertionError: If :py:attr:`payment.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`address.authorizenet_id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: An Authorizenet subscription id.
        :rtype: :py:obj:`int`

        """
        assert self.payment.authorizenet_id, "Payment id was not set."
        assert self.address.authorizenet_id, "Address id was not set."

        subscription_profile: SubscriptionProfile = SubscriptionProfile(
            name=f"{self.customer}'s {self.tier.name} Subscription",
            amount=self.get_amount_plus_tax(),
            schedule=self.generate_payment_schedule(timezone.now()),
            profile_id=self.customer.authorizenet_id,
            payment_id=self.payment.authorizenet_id,
            address_id=self.address.authorizenet_id,
        )
        return int(subscription_profile.id)

    def authorizenet_get_subscription_profile(self) -> SubscriptionProfile:
        """
        Returns the Authorizenet subscription profile for the subscription.

        :raises AssertionError: If :py:attr:`authorizenet_id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: A subscription profile.
        :rtype: :py:obj:`~terminusgps.authorizenet.profiles.SubscriptionProfile`

        """
        assert self.authorizenet_id, "Authorizenet id was not set."
        return SubscriptionProfile(id=self.authorizenet_id)

    def generate_monthly_payment_interval(
        self,
    ) -> apicontractsv1.paymentScheduleTypeInterval:
        """
        Generates a monthly charge payment interval for the subscription.

        :returns: A payment interval.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.paymentScheduleTypeInterval`

        """
        return apicontractsv1.paymentScheduleTypeInterval(
            length=1, unit=apicontractsv1.ARBSubscriptionUnitEnum.months
        )

    def generate_payment_schedule(
        self, start_date: datetime.datetime
    ) -> apicontractsv1.paymentScheduleType:
        """
        Generates a payment schedule for the subscription.

        :returns: A payment schedule.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.paymentScheduleType`

        """
        return apicontractsv1.paymentScheduleType(
            interval=self.generate_monthly_payment_interval(),
            startDate=start_date,
            totalOccurrences=self.total_months,
            trialOccurrences=self.trial_months,
        )
