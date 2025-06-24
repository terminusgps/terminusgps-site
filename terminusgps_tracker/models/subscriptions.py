import decimal

from authorizenet import apicontractsv1
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.controllers import (
    AuthorizenetControllerExecutionError,
)
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
            "tracker:subscription detail",
            kwargs={"customer_pk": self.customer.pk, "sub_pk": self.pk},
        )

    def delete(self, *args, **kwargs):
        """Cancels the subscription in Authorizenet before deleting the object."""
        try:
            sprofile = self.authorizenet_get_subscription_profile()
            sprofile.delete()
        except AuthorizenetControllerExecutionError:
            print("Something went wrong with Authorizenet.")
        finally:
            super().delete(*args, **kwargs)

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

    def calculate_amount(self, add_tax: bool = True) -> decimal.Decimal:
        """
        Calculates and returns the total dollar amount for the subscription.

        :param add_tax: Whether or not to add tax to the calculated amount. Default is :py:obj:`True`.
        :type add_tax: :py:obj:`bool`
        :returns: The total dollar amount for the subscription.
        :rtype: :py:obj:`~decimal.Decimal`

        """
        amounts = []
        amounts.extend(self.get_total_unit_amounts())
        amounts.extend(self.get_total_feature_amounts())

        return (
            calculate_amount_plus_tax(decimal.Decimal(sum(amounts)))
            if add_tax
            else decimal.Decimal(sum(amounts))
        )

    def get_total_feature_amounts(self) -> list[decimal.Decimal]:
        """Returns a list of dollar amounts for features assigned to the subscription."""
        if not self.features.exists():
            return []
        return [f.calculate_amount() for f in self.features.all()]

    def get_total_unit_amounts(self) -> list[decimal.Decimal]:
        """Returns a list of dollar amounts for units assigned to the subscription."""
        if not self.customer.units.exists():
            return []
        return [u.calculate_amount() for u in self.customer.units.all()]

    def authorizenet_update_amount(
        self, sprofile: SubscriptionProfile, add_tax: bool = True
    ) -> SubscriptionProfile:
        """Recalculates and updates the subscription amount in Authorizenet."""
        new_amount = self.calculate_amount(add_tax=add_tax)
        sprofile.update(apicontractsv1.ARBSubscriptionType(amount=new_amount))
        return sprofile

    def authorizenet_update_payment(
        self, sprofile: SubscriptionProfile
    ) -> SubscriptionProfile:
        """Updates the payment method and shipping address for the subscription in Authorizenet."""
        sprofile.update(
            apicontractsv1.ARBSubscriptionType(
                profile=apicontractsv1.customerProfileIdType(
                    customerProfileId=str(
                        self.customer.authorizenet_profile_id
                    ),
                    customerPaymentProfileId=str(self.payment.pk),
                    customerAddressId=str(self.address.pk),
                )
            )
        )
        return sprofile

    def authorizenet_sync(self) -> SubscriptionProfile:
        """Syncs the subscription payment, address and status with Authorizenet."""
        sprofile = self.authorizenet_get_subscription_profile()
        self.authorizenet_sync_status(sprofile)
        self.authorizenet_sync_payment(sprofile)
        self.authorizenet_sync_address(sprofile)
        return sprofile

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
        """Returns :py:obj:`True` if the subscription is missing a payment or an address."""
        return not bool(self.payment or self.address)

    def authorizenet_get_subscription_profile(self) -> SubscriptionProfile:
        """Returns a :py:obj:`~terminusgps.authorizenet.profiles.subscriptions.SubscriptionProfile` for the subscription."""
        return SubscriptionProfile(
            customer_profile_id=self.customer.authorizenet_profile_id,
            id=self.pk,
        )

    @staticmethod
    def authorizenet_get_transaction_list(
        sprofile: SubscriptionProfile,
    ) -> list[dict[str, str]]:
        """Retrieves and returns a transaction list for a subscription profile."""
        return sprofile.transactions


class SubscriptionFeature(models.Model):
    """A subscription feature for a customer subscription."""

    name = models.CharField(max_length=64)
    """Subscription feature name."""
    desc = models.TextField(
        max_length=1024, null=True, blank=True, default=None
    )
    """Subscription feature description."""
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=9.99)
    """Subscription feature $ amount."""
    total = models.PositiveIntegerField(default=1)
    """Subscription feature total."""

    def __str__(self) -> str:
        """Returns the subscription feature name."""
        return f"{self.total}x {self.name}"

    def get_amount_display(self) -> str:
        """Returns the dollar amount of the feature."""
        return f"${self.amount}"

    def calculate_amount(self) -> decimal.Decimal:
        """Returns the dollar amount times the total for the subscription feature."""
        return self.amount * self.total


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
        """Returns the dollar amount of the subscription tier."""
        return f"${self.amount}"
