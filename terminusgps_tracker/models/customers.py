import pyotp
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)
from terminusgps.wialon.items import WialonResource, WialonUnit, WialonUser
from terminusgps.wialon.session import WialonSession


class Customer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    email_verified = models.BooleanField(default=False)
    """Whether or not the user has completed email verification."""
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    """Email one-time password."""
    authorizenet_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    """An Authorizenet customer profile id."""
    wialon_user_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    """A Wialon user id."""
    wialon_resource_id = models.PositiveIntegerField(
        null=True, blank=True, default=None
    )
    """A Wialon resource id."""

    def __str__(self) -> str:
        return self.user.username

    def save(self, **kwargs) -> None:
        if not self.authorizenet_id:
            customer_profile = CustomerProfile(
                merchant_id=self.user.pk,
                id=None,
                email=self.user.username,
                desc=f"{timezone.now():%Y-%m-%d %H:%M:%S}: Created by the Terminus GPS Tracker application",
            )
            self.authorizenet_id = customer_profile.id
        super().save(**kwargs)

    def authorizenet_get_customer_profile(self) -> CustomerProfile:
        """Returns a :py:obj:`~terminusgps.authorizenet.profiles.CustomerProfile` for the customer."""
        assert self.authorizenet_id is not None, "'authorizenet_id' wasn't set."
        return CustomerProfile(merchant_id=self.user.pk, id=self.authorizenet_id)

    def generate_email_otp(self, duration: int = 500) -> str:
        """
        Generates an OTP to be verified via email.

        :param duration: How long (in seconds) the OTP will be valid for.
        :type duration: :py:obj:`int`
        :returns: A OTP.
        :rtype: :py:obj:`str`

        """
        return pyotp.TOTP(pyotp.random_base32(), interval=duration).now()

    @transaction.atomic
    def authorizenet_sync_payment_profiles(self) -> None:
        customer_profile: CustomerProfile = self.authorizenet_get_customer_profile()
        payment_ids: set[int] = set(customer_profile.payment_profile_ids)
        for profile_id in payment_ids.difference(
            list(self.payments.all().values_list("authorizenet_id", flat=True))
        ):
            CustomerPaymentMethod.objects.create(
                customer=self, authorizenet_id=profile_id
            )

    @transaction.atomic
    def authorizenet_sync_address_profiles(self) -> None:
        customer_profile: CustomerProfile = self.authorizenet_get_customer_profile()
        address_ids: set[int] = set(customer_profile.address_profile_ids)
        for profile_id in address_ids.difference(
            list(self.addresses.all().values_list("authorizenet_id", flat=True))
        ):
            CustomerShippingAddress.objects.create(
                customer=self, authorizenet_id=profile_id
            )

    def wialon_get_username(self, session: WialonSession) -> str | None:
        """
        Returns the customer's Wialon user username.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: The customer's Wialon user username, if it exists.
        :rtype: :py:obj:`str` | :py:obj:`None`

        """
        if self.wialon_user_id:
            user = WialonUser(id=self.wialon_user_id, session=session)
            return user.name

    def wialon_disable_account(self, session: WialonSession) -> None:
        """
        Disables the customer's Wialon account.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :raises WialonError: If something goes wrong calling the Wialon API.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.wialon_resource_id:
            resource: WialonResource = WialonResource(
                id=self.wialon_resource_id, session=session
            )
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
        if self.wialon_resource_id:
            resource: WialonResource = WialonResource(
                id=self.wialon_resource_id, session=session
            )
            if resource.is_account:
                resource.enable_account()


class CustomerAsset(models.Model):
    customer = models.ForeignKey(
        "terminusgps_tracker.Customer", on_delete=models.CASCADE, related_name="assets"
    )
    """A customer."""
    name = models.CharField(max_length=128, null=True, blank=True, default=None)
    """An identifiable name."""
    wialon_id = models.PositiveIntegerField()
    """A Wialon unit id."""

    def __str__(self) -> str:
        return f"Asset #{self.pk}"

    @transaction.atomic
    def wialon_sync_name(self, session: WialonSession) -> None:
        unit: WialonUnit = self.wialon_get_unit(session)
        if self.name is None or self.name != unit.name:
            self.name = unit.name
            self.save()
        else:
            unit.rename(self.name)

    def wialon_get_unit(self, session: WialonSession) -> WialonUnit:
        """
        Returns a :py:obj:`~terminusgps.wialon.items.WialonUnit` for the asset.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :raises AssertionError: If :py:attr:`wialon_id` wasn't set.
        :returns: A Wialon unit.
        :rtype: :py:obj:`~terminusgps.wialon.items.WialonUnit`

        """
        assert self.wialon_id is not None, "'wialon_id' wasn't set."
        return WialonUnit(id=self.wialon_id, session=session)

    def wialon_unit_exists(self, session: WialonSession) -> bool:
        """
        Determines whether or not the unit exists in Wialon.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Whether or not the unit exists.
        :rtype: :py:obj:`bool`

        """
        if not self.wialon_id:
            return False
        return self.wialon_get_unit(session).exists


class CustomerPaymentMethod(models.Model):
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

    def __str__(self) -> str:
        return f"Payment Method #{self.authorizenet_id}"

    def get_absolute_url(self) -> str:
        return reverse("detail payment", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """Deletes the payment profile in Authorizenet before deleting the object."""
        if self.authorizenet_id:
            payment_profile = self.authorizenet_get_payment_profile()
            payment_profile.delete()
        return super().delete(*args, **kwargs)

    def authorizenet_get_payment_profile(self) -> PaymentProfile:
        """
        Returns the Authorizenet payment profile for the payment method.

        :raises AssertionError: If the customer's Authorizenet profile id wasn't set.
        :returns: An Authorizenet payment profile.
        :rtype: :py:obj:`~terminusgps.authorizenet.profiles.PaymentProfile`

        """
        assert self.customer.authorizenet_id, "Customer profile id wasn't set."
        return PaymentProfile(
            merchant_id=self.customer.user.pk,
            customer_profile_id=self.customer.authorizenet_id,
            id=self.authorizenet_id,
            default=self.default,
        )


class CustomerShippingAddress(models.Model):
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
        verbose_name_plural = "customer shipping addresses"

    def __str__(self) -> str:
        return f"Shipping Address #{self.authorizenet_id}"

    def save(self, **kwargs) -> None:
        super().save(**kwargs)

    def get_absolute_url(self) -> str:
        return reverse("detail address", kwargs={"pk": self.pk})

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        """Deletes the address profile in Authorizenet before deleting the object."""
        if self.authorizenet_id:
            address_profile = self.authorizenet_get_address_profile()
            address_profile.delete()
        return super().delete(*args, **kwargs)

    def authorizenet_get_address_profile(self) -> AddressProfile:
        """
        Returns the Authorizenet address profile for the shipping address.

        :raises AssertionError: If the customer's Authorizenet profile id wasn't set.
        :returns: An Authorizenet address profile.
        :rtype: :py:obj:`~terminusgps.authorizenet.profiles.AddressProfile`

        """
        assert self.customer.authorizenet_id, "Customer profile id wasn't set."
        return AddressProfile(
            merchant_id=self.customer.user.pk,
            customer_profile_id=self.customer.authorizenet_id,
            id=self.authorizenet_id,
            default=self.default,
        )
