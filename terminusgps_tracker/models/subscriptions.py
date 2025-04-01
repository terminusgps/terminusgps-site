from authorizenet import apicontractsv1
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.profiles import SubscriptionProfile


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
        if not self.amount:
            return self.name
        return f"{self.get_amount_display()} {self.name}"


class CustomerSubscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        CANCELED = "canceled", _("Canceled")
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
        choices=[(12, _("12 months")), (24, _("24 months"))], default=12
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
    )
    """Current subscription tier."""
    payment = models.ForeignKey(
        "terminusgps_tracker.CustomerPaymentMethod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """A payment method."""
    address = models.ForeignKey(
        "terminusgps_tracker.CustomerShippingAddress",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )
    """A shipping address."""
    status = models.CharField(
        max_length=16,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.SUSPENDED,
    )
    """Current Authorizenet subscription status."""

    class Meta:
        constraints = []

    def __str__(self) -> str:
        return f"{self.customer}'s Subscription"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the subscription's detail view."""
        return reverse("detail subscription", kwargs={"pk": self.pk})

    @transaction.atomic
    def authorizenet_delete_subscription(self) -> None:
        sub_profile = self.authorizenet_get_subscription_profile()
        sub_profile.delete()

    @transaction.atomic
    def authorizenet_refresh_status(self) -> None:
        """Refreshes the subscription status from Authorizenet."""
        self.status = self.authorizenet_get_subscription_profile().status
        self.save()

    @transaction.atomic
    def authorizenet_create_subscription(self) -> None:
        """
        Creates a subscription in Authorizenet.

        :raises AssertionError: If :py:attr:`payment.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`address.authorizenet_id` wasn't set.
        :raises ControllerExecutionError: If something goes wrong with an Authorizenet API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.payment.authorizenet_id, "Payment id was not set."
        assert self.address.authorizenet_id, "Address id was not set."

        sub_profile = SubscriptionProfile(
            name=f"{self.customer.user.username}'s {self.tier} Subscription",
            amount=self.tier.amount,
            schedule=self.generate_payment_schedule(),
            profile_id=self.customer.authorizenet_id,
            payment_id=self.payment.authorizenet_id,
            address_id=self.address.authorizenet_id,
        )
        self.authorizenet_id = sub_profile.id

    def authorizenet_get_subscription_profile(self) -> SubscriptionProfile:
        """
        Returns the Authorizenet subscription profile for the subscription.

        :raises AssertionError: If :py:attr`authorizenet_id` wasn't set.
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

    def generate_payment_schedule(self) -> apicontractsv1.paymentScheduleType:
        """
        Generates a payment schedule for the subscription.

        :returns: A payment schedule.
        :rtype: :py:obj:`~authorizenet.apicontractsv1.paymentScheduleType`

        """
        return apicontractsv1.paymentScheduleType(
            interval=self.generate_monthly_payment_interval(),
            startDate=timezone.now(),
            totalOccurrences=self.total_months,
            trialOccurrences=self.trial_months,
        )
