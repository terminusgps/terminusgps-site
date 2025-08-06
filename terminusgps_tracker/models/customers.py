import datetime
import decimal
import logging
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet import profiles
from terminusgps.wialon import flags
from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSession

logger = logging.getLogger(__name__)


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

    def calculate_subscription_amount(self) -> decimal.Decimal:
        unit_list = CustomerWialonUnit.objects.filter(
            customer=self
        ).select_related("tier")
        if unit_list.count() == 0:
            return decimal.Decimal("0.00")
        return decimal.Decimal(
            sum(unit_list.values_list("tier__amount", flat=True))
        )

    def get_subscription_start_date(self) -> datetime.datetime | None:
        if self.subscription:
            return self.subscription.start_date.replace(
                hour=16, minute=0, tzinfo=ZoneInfo("US/Pacific")
            )

    def authorizenet_get_profile(self):
        """Returns the Authorizenet customer profile for the customer."""
        return profiles.get_customer_profile(
            self.authorizenet_profile_id, include_issuer_info=True
        )

    def authorizenet_sync(self) -> None:
        """Syncs customer payment methods and shipping addresses with Authorizenet."""
        self.authorizenet_sync_payment_methods()
        self.authorizenet_sync_shipping_addresses()

    def wialon_sync(self, session: WialonSession) -> WialonSession:
        """Syncs customer units with Wialon."""
        self.wialon_sync_units(session)
        return session

    @transaction.atomic
    def wialon_sync_units(self, session: WialonSession) -> None:
        local_objs = CustomerWialonUnit.objects.filter(customer=self)
        local_ids = local_objs.values_list("id", flat=True)
        remote_ids = self._wialon_get_remote_unit_ids(session)
        ids_to_create = set(remote_ids) - set(local_ids) if remote_ids else []
        ids_to_delete = set(local_ids) - set(remote_ids) if local_ids else []

        if ids_to_create:
            CustomerWialonUnit.objects.bulk_create(
                [
                    CustomerWialonUnit(id=id, customer=self)
                    for id in ids_to_create
                ],
                ignore_conflicts=True,
            )

        if ids_to_delete:
            CustomerWialonUnit.objects.filter(
                id__in=ids_to_delete, customer=self
            ).delete()

    @transaction.atomic
    def authorizenet_sync_payment_methods(self) -> None:
        local_objs = CustomerPaymentMethod.objects.filter(customer=self)
        local_ids = local_objs.values_list("id", flat=True)
        remote_ids = self._authorizenet_get_remote_payment_profile_ids()
        ids_to_create = set(remote_ids) - set(local_ids) if remote_ids else []
        ids_to_delete = set(local_ids) - set(remote_ids) if local_ids else []

        if ids_to_create:
            CustomerPaymentMethod.objects.bulk_create(
                [
                    CustomerPaymentMethod(id=id, customer=self)
                    for id in ids_to_create
                ],
                ignore_conflicts=True,
            )

        if ids_to_delete:
            CustomerPaymentMethod.objects.filter(
                id__in=ids_to_delete, customer=self
            ).delete()

    @transaction.atomic
    def authorizenet_sync_shipping_addresses(self) -> None:
        local_objs = CustomerShippingAddress.objects.filter(customer=self)
        local_ids = local_objs.values_list("id", flat=True)
        remote_ids = self._authorizenet_get_remote_address_profile_ids()
        ids_to_create = set(remote_ids) - set(local_ids) if remote_ids else []
        ids_to_delete = set(local_ids) - set(remote_ids) if local_ids else []

        if ids_to_create:
            CustomerShippingAddress.objects.bulk_create(
                [
                    CustomerShippingAddress(id=id, customer=self)
                    for id in ids_to_create
                ],
                ignore_conflicts=True,
            )

        if ids_to_delete:
            CustomerShippingAddress.objects.filter(
                id__in=ids_to_delete, customer=self
            ).delete()

    def _authorizenet_get_remote_address_profile_ids(self) -> list[int]:
        """Returns a list of address profile ids for the customer profile from Authorizenet."""
        cprofile = self.authorizenet_get_profile()
        if cprofile is None or not hasattr(cprofile.profile, "shipToList"):
            return []
        return [
            int(aprofile.customerAddressId)
            for aprofile in cprofile.profile.shipToList
        ]

    def _authorizenet_get_remote_payment_profile_ids(self) -> list[int]:
        """Returns a list of payment profile ids for the customer profile from Authorizenet."""
        cprofile = self.authorizenet_get_profile()
        if cprofile is None or not hasattr(
            cprofile.profile, "paymentProfiles"
        ):
            return []
        return [
            int(pprofile.customerPaymentProfileId)
            for pprofile in cprofile.profile.paymentProfiles
        ]

    def _wialon_get_remote_unit_ids(self, session: WialonSession) -> list[int]:
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
        return (
            self.name if not self.wialon_needs_sync() else f"Unit #{self.pk}"
        )

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

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the payment method's detail view."""
        return reverse(
            "tracker:payment detail",
            kwargs={"customer_pk": self.customer.pk, "payment_pk": self.pk},
        )

    def authorizenet_get_profile(self, include_issuer_info: bool = False):
        return profiles.get_customer_payment_profile(
            customer_profile_id=self.customer.authorizenet_profile_id,
            customer_payment_profile_id=self.pk,
            include_issuer_info=include_issuer_info,
        )

    def authorizenet_needs_sync(self) -> bool:
        """Returns whether or not the payment method is out of sync with Authorizenet."""
        return not all([self.cc_last_4, self.cc_type])

    @transaction.atomic
    def authorizenet_sync(self) -> None:
        """Sets the credit card type and last 4 digits for the payment method from Authorizenet."""
        self.cc_last_4 = self._authorizenet_get_credit_card_number()[-4:]
        self.cc_type = self._authorizenet_get_credit_card_type()

    def _authorizenet_get_credit_card_number(self) -> str:
        """Returns the (obfuscated) credit card number for the payment method, or 'XXXXXXXX' if not found."""
        pprofile = self.authorizenet_get_profile().paymentProfile
        if any(
            [
                pprofile is None,
                not hasattr(pprofile, "payment"),
                not hasattr(pprofile.payment, "creditCard"),
                not hasattr(pprofile.payment.creditCard, "cardNumber"),
            ]
        ):
            return "XXXXXXXX"
        return str(pprofile.payment.creditCard.cardNumber)

    def _authorizenet_get_credit_card_type(self) -> str:
        """Returns the credit card type for the payment method, or 'Unknown' if not found."""
        pprofile = self.authorizenet_get_profile().paymentProfile
        if any(
            [
                pprofile is None,
                not hasattr(pprofile, "payment"),
                not hasattr(pprofile.payment, "creditCard"),
                not hasattr(pprofile.payment.creditCard, "cardType"),
            ]
        ):
            return "Unknown"
        return str(pprofile.payment.creditCard.cardType)


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

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the shipping address' detail view."""
        return reverse(
            "tracker:address detail",
            kwargs={"customer_pk": self.customer.pk, "address_pk": self.pk},
        )

    def authorizenet_get_profile(self):
        return profiles.get_customer_shipping_address(
            customer_profile_id=self.customer.authorizenet_profile_id,
            customer_address_profile_id=self.pk,
        )

    def authorizenet_needs_sync(self) -> bool:
        """Returns whether or not the shipping address is out of sync with Authorizenet."""
        return not all([self.street])

    @transaction.atomic
    def authorizenet_sync(self) -> None:
        """Syncs shipping address data with Authorizenet."""
        self.street = self._authorizenet_get_street()

    def _authorizenet_get_street(self) -> str:
        """Returns the street for the shipping address, or 'Unknown' if not found."""
        aprofile = self.authorizenet_get_profile()
        if aprofile is None or not hasattr(aprofile.address, "address"):
            return "Unknown"
        return str(aprofile.address.address)
