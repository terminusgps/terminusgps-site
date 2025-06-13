from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)
from terminusgps.wialon.items import WialonResource, WialonUnit
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
        current_payment_ids = set(
            CustomerPaymentMethod.objects.filter(customer=self).values_list(
                "id", flat=True
            )
        )
        new_payment_objs = [
            CustomerPaymentMethod(id=id, customer=self)
            for id in self.authorizenet_get_payment_profile_ids()
            if id not in current_payment_ids
        ]
        if new_payment_objs:
            CustomerPaymentMethod.objects.bulk_create(
                new_payment_objs, ignore_conflicts=True
            )

    @transaction.atomic
    def authorizenet_sync_address_profiles(self) -> None:
        """Retrieves address profiles from Authorizenet and creates customer shipping addresses based on them."""
        current_address_ids = set(
            CustomerShippingAddress.objects.filter(customer=self).values_list(
                "id", flat=True
            )
        )
        new_address_objs = [
            CustomerShippingAddress(id=id, customer=self)
            for id in self.authorizenet_get_address_profile_ids()
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

    def authorizenet_get_address_profile_ids(self) -> list[int]:
        """Returns a list of address profile ids for the customer profile from Authorizenet."""
        return (
            self.authorizenet_get_customer_profile().get_address_profile_ids()
        )

    def authorizenet_get_payment_profile_ids(self) -> list[int]:
        """Returns a list of payment profile ids for the customer profile from Authorizenet."""
        return (
            self.authorizenet_get_customer_profile().get_payment_profile_ids()
        )

    def wialon_get_remaining_days(self) -> int:
        """Returns the remaining days for the customer's Wialon account."""
        if not self.wialon_resource_id:
            return 0
        with WialonSession() as session:
            resource = WialonResource(self.wialon_resource_id, session=session)
            return resource.get_remaining_days()


class CustomerWialonUnit(models.Model):
    """A Wialon unit for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon unit id."""
    name = models.CharField(max_length=64, null=True, blank=True, default=None)
    """Wialon unit name."""
    imei = models.CharField(max_length=19, null=True, blank=True, default=None)
    """Wialon unit IMEI number."""
    vin = models.CharField(max_length=17, null=True, blank=True, default=None)
    """Wialon unit VIN number."""
    tier = models.ForeignKey(
        "terminusgps_tracker.SubscriptionTier", on_delete=models.CASCADE
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
        """Returns the unit name if set, otherwise 'Unit #<pk>'."""
        return self.name if self.name else f"Unit #{self.pk}"

    def save(self, **kwargs) -> None:
        """Syncs the unit's data with the Wialon API if necessary."""
        if self.wialon_needs_sync():
            with WialonSession() as session:
                self.wialon_sync(session)
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the unit's detail view."""
        return reverse("tracker:unit detail", kwargs={"pk": self.pk})

    def wialon_needs_sync(self) -> bool:
        """Whether or not the unit needs to sync data with the Wialon API."""
        return any([not self.name, not self.imei, not self.vin])

    @transaction.atomic
    def wialon_sync(self, session: WialonSession) -> WialonSession:
        """Syncs the unit's data using the Wialon API."""
        unit = WialonUnit(id=self.pk, session=session)
        self.name = unit.name
        self.imei = unit.imei_number
        self.vin = unit.pfields.get("vin")
        return session


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

    def authorizenet_get_profile(self) -> dict:
        """Returns payment profile data from Authorizenet."""
        response = PaymentProfile(
            customer_profile_id=str(self.customer.authorizenet_profile_id),
            id=str(self.pk),
        )._authorizenet_get_payment_profile(issuer_info=True)
        return response if response is not None else {}

    def authorizenet_get_last_4(self) -> int | None:
        """Returns the last 4 digits of the payment method credit card."""
        return PaymentProfile(
            customer_profile_id=str(self.customer.authorizenet_profile_id),
            id=str(self.pk),
        ).last_4


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

    def authorizenet_get_profile(self) -> dict:
        """Returns address profile data from Authorizenet."""
        response = AddressProfile(
            customer_profile_id=str(self.customer.authorizenet_profile_id),
            id=str(self.pk),
        )._authorizenet_get_shipping_address()
        return response if response is not None else {}
