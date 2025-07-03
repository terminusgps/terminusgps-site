import decimal

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.constants import ANET_XMLNS
from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)
from terminusgps.wialon import flags
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

    def authorizenet_get_customer_profile(self) -> CustomerProfile:
        """Returns the Authorizenet customer profile for the customer."""
        return CustomerProfile(
            id=str(self.authorizenet_profile_id),
            merchant_id=str(self.user.pk),
            email=self.user.email if self.user.email else self.user.username,
        )

    def authorizenet_get_current_address_ids(self) -> list[int]:
        """Returns a list of address profile ids for the customer profile from Authorizenet."""
        cprofile: CustomerProfile = self.authorizenet_get_customer_profile()
        return cprofile.get_address_profile_ids()

    def authorizenet_get_current_payment_ids(self) -> list[int]:
        """Returns a list of payment profile ids for the customer profile from Authorizenet."""
        cprofile: CustomerProfile = self.authorizenet_get_customer_profile()
        return cprofile.get_payment_profile_ids()

    def wialon_get_current_unit_ids(self, session: WialonSession) -> list[int]:
        """Returns a list of current customer unit ids from Wialon."""
        response = session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit",
                    "propName": "sys_billing_account_guid,sys_id",
                    "propValueMask": f"={self.wialon_resource_id},*",
                    "sortType": "sys_id",
                    "propType": "property,property",
                    "or_logic": int(False),
                },
                "force": 0,
                "flags": flags.DataFlag.UNIT_BASE,
                "from": 0,
                "to": 0,
            }
        )

        if not response:
            return []
        return [int(unit.get("id")) for unit in response.get("items", {})]

    @transaction.atomic
    def wialon_sync_units(
        self, session: WialonSession
    ) -> list["CustomerWialonUnit"]:
        """Retrieves unit ids from Wialon and creates customer units based on them."""
        remote_unit_ids = set(self.wialon_get_current_unit_ids(session))
        local_unit_ids = set(
            CustomerWialonUnit.objects.filter(customer=self).values_list(
                "id", flat=True
            )
        )
        new_unit_objs = [
            CustomerWialonUnit(id=id, customer=self)
            for id in remote_unit_ids - local_unit_ids
        ]

        if not new_unit_objs:
            return []
        return CustomerWialonUnit.objects.bulk_create(
            new_unit_objs, ignore_conflicts=True
        )

    @transaction.atomic
    def authorizenet_sync_payment_profiles(
        self,
    ) -> list["CustomerPaymentMethod"]:
        """Retrieves payment profiles from Authorizenet and creates customer payment methods based on them."""
        remote_payment_ids = set(self.authorizenet_get_current_payment_ids())
        local_payment_ids = set(
            CustomerPaymentMethod.objects.filter(customer=self).values_list(
                "id", flat=True
            )
        )
        new_payment_objs = [
            CustomerPaymentMethod(id=id, customer=self)
            for id in remote_payment_ids - local_payment_ids
        ]

        if not new_payment_objs:
            return []
        return CustomerPaymentMethod.objects.bulk_create(
            new_payment_objs, ignore_conflicts=True
        )

    @transaction.atomic
    def authorizenet_sync_address_profiles(
        self,
    ) -> list["CustomerShippingAddress"]:
        """Retrieves address profiles from Authorizenet and creates customer shipping addresses based on them."""
        remote_address_ids = set(self.authorizenet_get_current_address_ids())
        local_address_ids = set(
            CustomerShippingAddress.objects.filter(customer=self).values_list(
                "id", flat=True
            )
        )
        new_address_objs = [
            CustomerShippingAddress(id=id, customer=self)
            for id in remote_address_ids - local_address_ids
        ]

        if not new_address_objs:
            return []
        return CustomerShippingAddress.objects.bulk_create(
            new_address_objs, ignore_conflicts=True
        )


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
        "terminusgps_tracker.SubscriptionTier", on_delete=models.PROTECT
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
        return f"Unit #{self.pk}" if not self.name else self.name

    def save(self, **kwargs) -> None:
        """Syncs the unit's data with the Wialon API if necessary."""
        if self.wialon_needs_sync():
            with WialonSession() as session:
                self.wialon_sync(session)
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the unit's list detail view."""
        return reverse(
            "tracker:unit list detail",
            kwargs={"customer_pk": self.customer.pk, "unit_pk": self.pk},
        )

    def wialon_needs_sync(self) -> bool:
        """Returns whether or not the unit needs to sync data with the Wialon API."""
        return not all([self.name, self.imei])

    @transaction.atomic
    def wialon_sync(self, session: WialonSession) -> WialonSession:
        """Syncs the unit's data using the Wialon API."""
        unit = WialonUnit(id=self.pk, session=session)
        self.name = unit.name
        self.imei = unit.imei_number
        self.vin = unit.pfields.get("vin")
        return session

    def calculate_amount(self) -> decimal.Decimal:
        """Returns the dollar amount for the unit."""
        return self.tier.amount


class CustomerPaymentMethod(models.Model):
    """A payment method for a customer."""

    id = models.PositiveBigIntegerField(primary_key=True)
    """Authorizenet customer payment profile id."""
    default = models.BooleanField(default=False)
    """Whether or not the payment method is set as default."""
    cc_last_4 = models.CharField(
        max_length=4, default=None, null=True, blank=True
    )
    """Last 4 digits of the payment method credit card."""
    cc_type = models.CharField(
        max_length=16, default=None, null=True, blank=True
    )
    """Merchant associated with the credit card."""
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
        return (
            f"{self.cc_type} ending in {self.cc_last_4}"
            if not self.authorizenet_needs_sync()
            else f"Payment Method #{self.pk}"
        )

    def save(self, **kwargs) -> None:
        """Syncs payment method data with Authorizenet if necessary."""
        if self.authorizenet_needs_sync():
            self.authorizenet_sync()
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the payment method's detail view."""
        return reverse(
            "tracker:payment detail",
            kwargs={"customer_pk": self.customer.pk, "payment_pk": self.pk},
        )

    @transaction.atomic
    def authorizenet_sync(self) -> None:
        """Sets the credit card type and last 4 digits for the payment method from Authorizenet."""
        self.cc_last_4 = str(self.authorizenet_get_credit_card_number())[-4:]
        self.cc_type = str(self.authorizenet_get_credit_card_type())

    def authorizenet_needs_sync(self) -> bool:
        """Returns whether or not the payment method is out of sync with Authorizenet."""
        return not all([self.cc_last_4, self.cc_type])

    def authorizenet_get_profile(self):
        """Returns payment profile data from Authorizenet."""
        # TODO: Add type hints
        response = PaymentProfile(
            customer_profile_id=str(self.customer.authorizenet_profile_id),
            id=str(self.pk),
        )._authorizenet_get_payment_profile(issuer_info=True)
        return (
            response.find(f"{ANET_XMLNS}paymentProfile")
            if response is not None
            else None
        )

    def authorizenet_get_credit_card_number(self) -> str:
        """Returns the (obfuscated) credit card number for the payment method."""
        response = self.authorizenet_get_profile()

        if response is None:
            return "XXXXXXXX"
        return (
            response.find(f"{ANET_XMLNS}payment")
            .find(f"{ANET_XMLNS}creditCard")
            .find(f"{ANET_XMLNS}cardNumber")
        )

    def authorizenet_get_credit_card_type(self) -> str:
        """Returns the credit card type for the payment method."""
        response = self.authorizenet_get_profile()

        if response is None:
            return "Unknown"
        return (
            response.find(f"{ANET_XMLNS}payment")
            .find(f"{ANET_XMLNS}creditCard")
            .find(f"{ANET_XMLNS}cardType")
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
    street = models.CharField(
        max_length=64, default=None, blank=True, null=True
    )
    """Shipping address street."""

    class Meta:
        verbose_name = _("customer shipping address")
        verbose_name_plural = _("customer shipping addresses")

    def __str__(self) -> str:
        return (
            self.street
            if not self.authorizenet_needs_sync()
            else f"Shipping Address #{self.pk}"
        )

    def save(self, **kwargs) -> None:
        """Syncs shipping address data with Authorizenet if necessary."""
        if self.authorizenet_needs_sync():
            self.authorizenet_sync()
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the shipping address' detail view."""
        return reverse(
            "tracker:address detail",
            kwargs={"customer_pk": self.customer.pk, "address_pk": self.pk},
        )

    @transaction.atomic
    def authorizenet_sync(self) -> None:
        """Syncs shipping address data with Authorizenet."""
        self.street = self.authorizenet_get_street()

    def authorizenet_needs_sync(self) -> bool:
        """Returns whether or not the shipping address is out of sync with Authorizenet."""
        return not all([self.street])

    def authorizenet_get_profile(self):
        """Returns address profile data from Authorizenet."""
        # TODO: Add type hints
        response = AddressProfile(
            customer_profile_id=str(self.customer.authorizenet_profile_id),
            id=str(self.pk),
        )._authorizenet_get_shipping_address()
        return (
            response.find(f"{ANET_XMLNS}address")
            if response is not None
            else None
        )

    def authorizenet_get_street(self) -> str:
        """Returns the street for the shipping address."""
        response = self.authorizenet_get_profile()

        if response is None:
            return "Unknown"
        return str(response.find(f"{ANET_XMLNS}address"))
