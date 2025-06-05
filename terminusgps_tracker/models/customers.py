from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)
from terminusgps.wialon.items import WialonUnit
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

    @transaction.atomic
    def authorizenet_sync_payment_profiles(self) -> None:
        """Retrieves payment profiles from Authorizenet and creates customer payment methods based on them."""
        cprofile = self.authorizenet_get_customer_profile()
        current_payment_ids = set(
            CustomerPaymentMethod.objects.filter(customer=self).values_list(
                "id", flat=True
            )
        )
        new_payment_objs = [
            CustomerPaymentMethod.objects.create(id=id, customer=self)
            for id in cprofile.get_payment_profile_ids()
            if id not in current_payment_ids
        ]
        if new_payment_objs:
            CustomerPaymentMethod.objects.bulk_create(
                new_payment_objs, ignore_conflicts=True
            )

    @transaction.atomic
    def authorizenet_sync_address_profiles(self) -> None:
        """Retrieves address profiles from Authorizenet and creates customer shipping addresses based on them."""
        cprofile = self.authorizenet_get_customer_profile()
        current_address_ids = set(
            CustomerShippingAddress.objects.filter(customer=self).values_list(
                "id", flat=True
            )
        )
        new_address_objs = [
            CustomerShippingAddress.objects.create(id=id, customer=self)
            for id in cprofile.get_address_profile_ids()
            if id not in current_address_ids
        ]
        if new_address_objs:
            CustomerShippingAddress.objects.bulk_create(
                new_address_objs, ignore_conflicts=True
            )

    def authorizenet_get_customer_profile(self) -> CustomerProfile:
        """Returns the Authorizenet customer profile for the customer."""
        return CustomerProfile(
            id=str(self.authorizenet_profile_id),
            merchant_id=str(self.user.pk),
            email=self.user.email if self.user.email else self.user.username,
        )

    def wialon_get_remaining_days(self) -> int:
        with WialonSession() as session:
            return session.wialon_api.account_get_account_data(
                **{"itemId": self.wialon_resource_id, "type": 1}
            ).get("daysCounter", 0)


class CustomerWialonUnit(models.Model):
    """A Wialon unit for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon unit id."""
    name = models.CharField(max_length=64, null=True, blank=True, default=None)
    """Wialon unit name."""
    imei = models.PositiveBigIntegerField(null=True, blank=True, default=None)
    """Wialon unit IMEI number."""
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
        return self.name if self.name else f"Unit #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse("tracker:unit detail", kwargs={"pk": self.pk})

    @transaction.atomic
    def wialon_sync(self) -> None:
        with WialonSession() as session:
            unit = WialonUnit(id=self.pk, session=session)
            self.name = unit.name
            self.imei = unit.imei_number


class CustomerPaymentMethod(models.Model):
    """A payment method for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet customer payment profile id."""
    default = models.BooleanField(default=False)
    """Whether or not the payment method is set as default."""
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

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the payment method's detail view."""
        return reverse("tracker:payment detail", kwargs={"pk": self.pk})

    def authorizenet_get_profile(self) -> dict | None:
        """Returns payment profile data from Authorizenet."""
        cprofile = self.customer.authorizenet_get_customer_profile()
        pprofile = PaymentProfile(customer_profile_id=cprofile.id, id=self.pk)
        return pprofile._authorizenet_get_payment_profile()

    def authorizenet_get_last_4(self) -> int:
        """Returns the last 4 digits of the payment method credit card."""
        pprofile = self.authorizenet_get_profile()
        return int(
            str(pprofile.paymentProfile.payment.creditCard.cardNumber)[-4:]
        )


class CustomerShippingAddress(models.Model):
    """A shipping address for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet customer shipping profile id."""
    default = models.BooleanField(default=False)
    """Whether or not the shipping address is set as default."""
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

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the shipping address' detail view."""
        return reverse("tracker:address detail", kwargs={"pk": self.pk})

    def authorizenet_get_profile(self) -> dict | None:
        """Returns address profile data from Authorizenet."""
        cprofile = self.customer.authorizenet_get_customer_profile()
        aprofile = AddressProfile(customer_profile_id=cprofile.id, id=self.pk)
        return aprofile._authorizenet_get_shipping_address()
