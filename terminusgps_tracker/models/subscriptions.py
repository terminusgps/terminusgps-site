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

from .customers import CustomerPaymentMethod, CustomerShippingAddress


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
        choices=SubscriptionFeatureAmount.choices, null=True, blank=True, default=None
    )
    """An amount for the subscription feature."""

    def __str__(self) -> str:
        """
        Returns a string representation the subscription feature in the format ``"<AMOUNT> <NAME>"``.

        If :py:attr:`amount` is :py:obj:`None`, instead returns ``"<NAME>"`` with no amount.

        :returns: A string.
        :rtype: :py:obj:`str`

        """
        if self.amount is not None:
            return f"{self.get_amount_display()} {self.name}"
        return self.name


class CustomerSubscription(models.Model):
    """An Authorizenet subscription for a customer."""

    class SubscriptionStatus(models.TextChoices):
        """An Authorizenet subscription status."""

        ACTIVE = "active", _("Active")
        """An active Authorizenet subscription."""
        CANCELED = "canceled", _("Canceled")
        """A canceled Authorizenet subscription."""
        UNBOUND = "unbound", _("Unbound")
        """An unbound Authorizenet subscription."""
        EXPIRED = "expired", _("Expired")
        """An expired Authorizenet subscription."""
        SUSPENDED = "suspended", _("Suspended")
        """A suspended Authorizenet subscription."""
        TERMINATED = "terminated", _("Terminated")
        """A terminated Authorizenet subscription."""

    customer = models.OneToOneField(
        "terminusgps_tracker.Customer",
        on_delete=models.PROTECT,
        related_name="subscription",
    )
    """A customer."""
    authorizenet_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    """An Authorizenet subscription id."""
    total_months = models.PositiveIntegerField(
        choices=[(12, _("1 year")), (24, _("2 years")), (9999, _("∞"))], default=9999
    )
    """Total number of months for the subscription."""
    trial_months = models.PositiveIntegerField(
        choices=[(0, _("0 months")), (12, _("12 months")), (24, _("24 months"))],
        default=0,
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

    class Meta:
        verbose_name = "subscription"
        verbose_name_plural = "subscriptions"

    def __str__(self) -> str:
        """Returns a string representation of the subscription in the format ``"<CUSTOMER NAME>'s Subscription"``."""
        return f"{self.customer}'s Subscription"

    def save(self, **kwargs) -> None:
        """
        Creates the subscription in Authorizenet if necessary.

        Syncs the subscription :py:attr:`status`, :py:attr:`payment` and :py:attr:`address` with Authorizenet.

        """
        if self.authorizenet_id and not self.tier:
            subscription_profile = self.authorizenet_get_subscription_profile()
            self.tier = SubscriptionTier.objects.create(
                name=subscription_profile.name,
                desc=f"{self.customer.user.first_name}'s Custom Subscription",
                amount=subscription_profile.amount,
            )
        elif not self.authorizenet_id and all([self.tier, self.address, self.payment]):
            self.authorizenet_id = self.authorizenet_create_subscription()

        if self.authorizenet_id:
            self.authorizenet_sync_status()
            self.authorizenet_sync_payment_method()
            self.authorizenet_sync_shipping_address()
        super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the subscription's detail view."""
        return reverse("tracker:detail subscription", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """Cancels the subscription in Authorizenet if necessary before deleting the object."""
        if self.authorizenet_id:
            self.authorizenet_sync_status()
        if self.authorizenet_id and self.status != self.SubscriptionStatus.CANCELED:
            self.authorizenet_cancel_subscription()
        return super().delete(*args, **kwargs)

    def clean(self) -> None:
        """Ensures :py:attr:`address` and :py:attr:`payments` are exclusive to the customer."""
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

    def calculate_amount_plus_tax(self) -> decimal.Decimal:
        """
        Returns the amount + tax for the subscription as a :py:obj:`~decimal.Decimal`.

        :raises AssertionError: If :py:attr:`tier` wasn't set.
        :returns: The subscription amount + tax.
        :rtype: :py:obj:`~decimal.Decimal`

        """
        assert self.tier, "Subscription tier wasn't set."

        return round(
            self.tier.amount + (self.tier.amount * settings.DEFAULT_TAX_RATE), ndigits=2
        )

    @transaction.atomic
    def authorizenet_sync_payment_method(self) -> None:
        """
        Creates or retrieves a :model:`terminusgps_tracker.CustomerPaymentMethod` based on the Authorizenet subscription profile and sets :py:attr:`payment` to it.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.authorizenet_id:
            subscription_profile = self.authorizenet_get_subscription_profile()
            self.payment, _ = CustomerPaymentMethod.objects.get_or_create(
                customer=self.customer, authorizenet_id=subscription_profile.payment_id
            )

    @transaction.atomic
    def authorizenet_sync_shipping_address(self) -> None:
        """
        Creates or retrieves a :model:`terminusgps_tracker.CustomerShippingAddress` based on the Authorizenet subscription profile and sets :py:attr:`address` to it.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.authorizenet_id:
            subscription_profile = self.authorizenet_get_subscription_profile()
            self.address, _ = CustomerShippingAddress.objects.get_or_create(
                customer=self.customer, authorizenet_id=subscription_profile.address_id
            )

    @transaction.atomic
    def authorizenet_sync_status(self) -> None:
        """
        Refreshes the subscription status from Authorizenet.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.authorizenet_id:
            subscription_profile = self.authorizenet_get_subscription_profile()
            self.status = subscription_profile.status

    def _generate_subscription_obj(
        self, add_tax: bool = True
    ) -> apicontractsv1.ARBSubscriptionType:
        """
        Generates a :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType` object based on the subscription for Authorizenet API calls.

        :raises AssertionError: If :py:attr:`address.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`payment.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`tier` wasn't set.
        :returns: An Authorizenet subscription object.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType`

        """
        assert self.address.authorizenet_id, "Address id was not set."
        assert self.payment.authorizenet_id, "Payment id was not set."
        assert self.tier, "Subscription tier wasn't set."

        return apicontractsv1.ARBSubscriptionType(
            name=f"{self.tier.name} Subscription",
            amount=self.calculate_amount_plus_tax() if add_tax else self.tier.amount,
            profile=apicontractsv1.customerProfileIdType(
                customerProfileId=str(self.customer.authorizenet_id),
                customerPaymentProfileId=str(self.payment.authorizenet_id),
                customerAddressId=str(self.address.authorizenet_id),
            ),
        )

    def authorizenet_update_subscription(self) -> None:
        """
        Updates the subscription in Authorizenet.

        :raises AssertionError: If :py:attr:`address.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`payment.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`tier` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.address.authorizenet_id, "Address id was not set."
        assert self.payment.authorizenet_id, "Payment id was not set."
        assert self.tier, "Subscription tier wasn't set."

        if self.authorizenet_id and "custom" in self.tier.name.lower():
            subscription_profile = self.authorizenet_get_subscription_profile()
            subscription_profile.update(self._generate_subscription_obj(add_tax=False))
        elif self.authorizenet_id:
            subscription_profile = self.authorizenet_get_subscription_profile()
            subscription_profile.update(self._generate_subscription_obj())

    def authorizenet_cancel_subscription(self) -> None:
        """
        Cancels a subscription in Authorizenet.

        :raises AuthorizenetControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.authorizenet_id:
            subscription_profile = self.authorizenet_get_subscription_profile()
            subscription_profile.delete()

    def authorizenet_create_subscription(
        self, start: datetime.datetime | None = None
    ) -> int:
        """
        Creates a subscription in Authorizenet.

        :param start: The start date for the subscription. Default is :py:func:`~django.utils.timezone.now`.
        :type start: :py:obj:`~datetime.datetime` | :py:obj:`None`
        :raises AssertionError: If :py:attr:`address.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`payment.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`tier` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: An Authorizenet subscription id.
        :rtype: :py:obj:`int`

        """
        assert self.address.authorizenet_id, "Address id was not set."
        assert self.payment.authorizenet_id, "Payment id was not set."
        assert self.tier, "Subscription tier wasn't set."

        now = start or timezone.now()
        subscription_obj = self._generate_subscription_obj()
        subscription_obj.paymentSchedule = self.generate_payment_schedule(now)
        subscription_obj.trialAmount = "0.00"
        subscription_profile = SubscriptionProfile(self.customer.authorizenet_id)
        return subscription_profile.create(subscription_obj)

    def authorizenet_get_subscription_profile(self) -> SubscriptionProfile:
        """
        Returns the Authorizenet subscription profile for the subscription.

        :raises AssertionError: If :py:attr:`authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`customer.authorizenet_id` wasn't set.
        :raises AuthorizenetControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: A subscription profile.
        :rtype: :py:obj:`~terminusgps.authorizenet.profiles.SubscriptionProfile`

        """
        assert self.authorizenet_id, "Authorizenet id was not set."
        assert self.customer.authorizenet_id, (
            "Customer profile authorizenet id was not set."
        )

        profile_id, sub_id = self.customer.authorizenet_id, self.authorizenet_id
        return SubscriptionProfile(customer_profile_id=profile_id, id=sub_id)

    def generate_payment_schedule(
        self,
        start_date: datetime.datetime,
        interval: apicontractsv1.paymentScheduleTypeInterval | None = None,
    ) -> apicontractsv1.paymentScheduleType:
        """
        Returns a payment schedule starting on ``start_date``.

        If ``interval`` is not provided, an interval charging the customer once per month is generated and used.

        :param start_date: The start date for the payment schedule.
        :type start_date: :py:obj:`~datetime.datetime`
        :param interval: An optional Authorizenet payment schedule interval object. The default interval charges a customer once a month.
        :type interval :py:obj:`~authorizenet.apicontractsv1.paymentScheduleIntervalType` | :py:obj:`None`
        :returns: A payment schedule object.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.paymentScheduleType`

        .. seealso:: :py:meth:`~terminusgps_tracker.models.CustomerSubscription.generate_monthly_payment_interval` for details on the default value of ``interval``.

        """
        return apicontractsv1.paymentScheduleType(
            interval=interval or self.generate_payment_interval(),
            startDate=start_date,
            totalOccurrences=self.total_months,
            trialOccurrences=self.trial_months,
        )

    @staticmethod
    def generate_payment_interval(
        length: int = 1,
        unit: apicontractsv1.ARBSubscriptionUnitEnum = apicontractsv1.ARBSubscriptionUnitEnum.months,
    ) -> apicontractsv1.paymentScheduleTypeInterval:
        """
        Returns a payment interval that charges a customer ``length`` time(s) every ``unit``.

        :param length: Total number of occurrences during one interval for the payment schedule. Default is ``1``.
        :type length: :py:obj:`int`
        :param unit: A unit of time. Default is :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionUnitEnum.months`.
        :type unit: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionUnitEnum`
        :returns: A payment interval.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.paymentScheduleTypeInterval`

        """
        return apicontractsv1.paymentScheduleTypeInterval(length=length, unit=unit)
