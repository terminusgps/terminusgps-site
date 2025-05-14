import pyotp
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.urls import reverse
from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)
from terminusgps.wialon.items import WialonResource
from terminusgps.wialon.session import WialonSession


class CustomerCoupon(models.Model):
    """A customer coupon."""

    redeemed = models.BooleanField(default=False)
    """Whether or not the coupon is redeemed."""
    percent_off = models.PositiveSmallIntegerField(
        default=15, validators=[MinValueValidator(15), MaxValueValidator(100)]
    )
    """The percentage off of a cost."""
    total_months = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    """Total number of months the coupon grants its percentage off for."""
    customer = models.ForeignKey(
        "terminusgps_tracker.Customer", on_delete=models.CASCADE, related_name="coupons"
    )
    """The customer the coupon can be redeemed by."""

    class Meta:
        verbose_name = "coupon"
        verbose_name_plural = "coupons"

    def __str__(self) -> str:
        """Returns the coupon in the format: <CUSTOMER EMAIL>'s <PERCENT_OFF>% off coupon."""
        return f"{self.customer.user.username}'s {self.percent_off}% off coupon"


class Customer(models.Model):
    """A customer."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    email_verified = models.BooleanField(default=False)
    """Whether or not the customer has completed email verification."""
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    """An email one-time password."""
    authorizenet_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    """An Authorizenet customer profile id."""
    wialon_user_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    """A Wialon user id."""
    wialon_resource_id = models.PositiveIntegerField(
        null=True, blank=True, default=None
    )
    """A Wialon resource id."""

    def __str__(self) -> str:
        """Returns the customer's username (an email address)."""
        return self.user.username

    def save(self, **kwargs) -> None:
        """Retrieves and/or creates an Authorizenet customer profile for the customer."""
        if not self.authorizenet_id:
            customer_profile: CustomerProfile = self.authorizenet_get_customer_profile()
            self.authorizenet_id = int(customer_profile.id)
        super().save(**kwargs)

    def generate_email_otp(self, duration: int = 500) -> str:
        """
        Generates an OTP to be verified via email.

        :param duration: How long (in seconds) the OTP will be valid for.
        :type duration: :py:obj:`int`
        :returns: A OTP.
        :rtype: :py:obj:`str`

        """
        return pyotp.TOTP(pyotp.random_base32(), interval=duration).now()

    def authorizenet_get_customer_profile(self) -> CustomerProfile:
        """
        Returns a customer profile for the customer.

        :returns: A customer profile object.
        :rtype: :py:obj:`~terminusgps.authorizenet.profiles.customers.CustomerProfile`

        """
        if self.authorizenet_id:
            return CustomerProfile(id=self.authorizenet_id)
        return CustomerProfile(merchant_id=str(self.user.pk), email=self.user.username)

    @transaction.atomic
    def authorizenet_sync_payment_profiles(self) -> None:
        """Creates :model:`terminusgps_tracker.CustomerPaymentMethod` objects for each payment profile present in Authorizenet but missing locally."""
        customer_profile: CustomerProfile = self.authorizenet_get_customer_profile()
        payment_ids: set[int] = set(customer_profile.get_payment_profile_ids())
        for profile_id in payment_ids.difference(
            self.payments.all().values_list("authorizenet_id", flat=True)
        ):
            CustomerPaymentMethod.objects.create(
                customer=self, authorizenet_id=profile_id
            )

    @transaction.atomic
    def authorizenet_sync_address_profiles(self) -> None:
        """Creates :model:`terminusgps_tracker.CustomerShippingAddress` objects for each address profile present in Authorizenet but missing locally."""
        customer_profile: CustomerProfile = self.authorizenet_get_customer_profile()
        address_ids: set[int] = set(customer_profile.get_address_profile_ids())
        for profile_id in address_ids.difference(
            self.addresses.all().values_list("authorizenet_id", flat=True)
        ):
            CustomerShippingAddress.objects.create(
                customer=self, authorizenet_id=profile_id
            )

    def wialon_disable_account(self, session: WialonSession) -> None:
        """
        Disables the customer's Wialon account.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :raises WialonError: If something goes wrong calling the Wialon API.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.wialon_resource_id is not None:
            resource = WialonResource(self.wialon_resource_id, session=session)
            if resource.is_account:
                resource.disable_account()

    def wialon_enable_account(self, session: WialonSession) -> None:
        """
        Enables the customer's Wialon account.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :raises WialonError: If something goes wrong calling the Wialon API.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.wialon_resource_id is not None:
            resource = WialonResource(self.wialon_resource_id, session=session)
            if resource.is_account:
                resource.enable_account()


class CustomerAsset(models.Model):
    """A customer Wialon unit."""

    customer = models.ForeignKey(
        "terminusgps_tracker.Customer", on_delete=models.CASCADE, related_name="assets"
    )
    """A customer."""
    name = models.CharField(max_length=128, null=True, blank=True, default=None)
    """An identifiable name."""
    wialon_id = models.PositiveIntegerField()
    """A Wialon unit id."""

    class Meta:
        verbose_name = "asset"
        verbose_name_plural = "assets"

    def __str__(self) -> str:
        """Returns the asset's id in format: ``'Asset #<pk>'``"""
        return f"Asset #{self.pk}"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the asset's detail view."""
        return reverse("tracker:detail asset", kwargs={"pk": self.pk})


class CustomerPaymentMethod(models.Model):
    """A customer payment method."""

    customer = models.ForeignKey(
        "terminusgps_tracker.Customer",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    """A customer."""
    authorizenet_id = models.PositiveIntegerField()
    """An Authorizenet payment profile id."""
    default = models.BooleanField(default=False)
    """Whether or not the payment method is set as default."""

    class Meta:
        verbose_name = "payment method"
        verbose_name_plural = "payment methods"

    def __str__(self) -> str:
        """Returns the payment method id in format: ``'Payment Method #<authorizenet_id>'``."""
        return f"Payment Method #{self.authorizenet_id}"

    def get_absolute_url(self) -> str:
        """Returns a URL to the payment method's detail view."""
        return reverse("tracker:detail payment", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """Deletes the payment profile in Authorizenet before deleting the object."""
        if self.customer.authorizenet_id and self.authorizenet_id:
            payment_profile = self.authorizenet_get_payment_profile()
            payment_profile.delete()
        return super().delete(*args, **kwargs)

    def authorizenet_get_payment_profile(self) -> PaymentProfile:
        """
        Returns the Authorizenet payment profile for the payment method.

        :raises AssertionError: If :py:attr:`customer.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`authorizenet_id` wasn't set.
        :returns: An Authorizenet payment profile.
        :rtype: :py:obj:`~terminusgps.authorizenet.profiles.PaymentProfile`

        """
        assert self.customer.authorizenet_id, "Customer profile id wasn't set."
        assert self.authorizenet_id, "Payment method id wasn't set."

        return PaymentProfile(
            customer_profile_id=self.customer.authorizenet_id,
            id=self.authorizenet_id,
            default=self.default,
        )


class CustomerShippingAddress(models.Model):
    """A customer shipping address."""

    customer = models.ForeignKey(
        "terminusgps_tracker.Customer",
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    """A customer."""
    authorizenet_id = models.PositiveIntegerField()
    """An Authorizenet shipping address id."""
    default = models.BooleanField(default=False)
    """Whether or not the shipping address is set as default."""

    class Meta:
        verbose_name = "shipping address"
        verbose_name_plural = "shipping addresses"

    def __str__(self) -> str:
        """Returns the shipping address id in format: ``'Shipping Address #<authorizenet_id>'``."""
        return f"Shipping Address #{self.authorizenet_id}"

    def get_absolute_url(self) -> str:
        """Returns a URL for the shipping address' detail view."""
        return reverse("tracker:detail address", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """Deletes the address profile in Authorizenet before deleting the object."""
        if self.customer.authorizenet_id and self.authorizenet_id:
            address_profile = self.authorizenet_get_address_profile()
            address_profile.delete()
        return super().delete(*args, **kwargs)

    def authorizenet_get_address_profile(self) -> AddressProfile:
        """
        Returns an Authorizenet address profile for the shipping address.

        :raises AssertionError: If :py:attr:`customer.authorizenet_id` wasn't set.
        :raises AssertionError: If :py:attr:`authorizenet_id` wasn't set.
        :returns: An Authorizenet address profile.
        :rtype: :py:obj:`~terminusgps.authorizenet.profiles.AddressProfile`

        """
        assert self.customer.authorizenet_id, "Customer profile id wasn't set."
        assert self.authorizenet_id, "Shipping address id wasn't set."

        return AddressProfile(
            customer_profile_id=self.customer.authorizenet_id,
            id=self.authorizenet_id,
            default=self.default,
        )
