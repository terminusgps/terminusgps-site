import datetime

from authorizenet import apicontractsv1
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.profiles import SubscriptionProfile
from terminusgps.authorizenet.utils import (
    calculate_amount_plus_tax,
    generate_monthly_subscription_schedule,
)

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

    def authorizenet_get_profile(self) -> SubscriptionProfile:
        """Returns the Authorizenet subscription profile for the subscription."""
        return SubscriptionProfile(
            customer_profile_id=str(self.customer.authorizenet_profile_id),
            id=str(self.pk),
        )

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
            self.generate_arb_subscription()
        )

    def authorizenet_get_transactions(self) -> list[dict[str, str]]:
        """Returns a list of subscription transactions from Authorizenet."""
        return self.authorizenet_get_profile().transactions

    def generate_arb_subscription(
        self, start_date: datetime.date | None = None
    ) -> apicontractsv1.ARBSubscriptionType:
        """
        Generates and returns an :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType` for Authorizenet API calls.

        If ``start_date`` is provided, adds an infinite monthly payment schedule to the subscription starting on that date.

        :param start_date: A start date for the subscription. Default is :py:obj:`None`
        :type start_date: :py:obj:`~datetime.date` | :py:obj:`None`
        :returns: A subscription object for Authorizenet API calls.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.ARBSubscriptionType`

        """
        arb_sub = apicontractsv1.ARBSubscriptionType()
        arb_sub.name = self._generate_arb_subscription_name()
        arb_sub.amount = self._generate_arb_subscription_amount()
        arb_sub.trialAmount = self._generate_arb_subscription_trial_amount()
        arb_sub.profile = self._generate_arb_subscription_customer_profile()

        if start_date:
            arb_sub.paymentSchedule = generate_monthly_subscription_schedule(
                start_date, total_occurrences=9999, trial_occurrences=0
            )
        return arb_sub

    def _generate_arb_subscription_trial_amount(self) -> str:
        """Returns ``"0.00"``."""
        return str(0.00)

    def _generate_arb_subscription_amount(self, taxed: bool = True) -> str:
        """
        Generates and returns an amount string for the subscription.

        :param taxed: Whether or not to add tax to the amount.
        :type taxed: :py:obj:`bool`
        :returns: A subscription amount string.
        :rtype: :py:obj:`str`

        """
        return str(
            calculate_amount_plus_tax(self.tier.amount)
            if taxed
            else self.tier.amount
        )

    def _generate_arb_subscription_name(self) -> str:
        """Generates and returns a name for the subscription."""
        return f"{self.tier} Subscription"

    def _generate_arb_subscription_customer_profile(
        self,
    ) -> apicontractsv1.customerProfileIdType:
        """Generates and returns a :py:obj:`~authorizenet.apicontractsv1.customerProfileIdType` for the subscription."""
        return apicontractsv1.customerProfileIdType(
            customerProfileId=str(self.customer.authorizenet_profile_id),
            customerPaymentProfileId=str(self.payment.id),
            customerAddressId=str(self.address.id),
        )
