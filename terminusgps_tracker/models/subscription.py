from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Money

from authorizenet.apicontractsv1 import (
    createCustomerPaymentProfileRequest,
    createCustomerPaymentProfileResponse,
    createCustomerShippingAddressRequest,
    createCustomerShippingAddressResponse,
    customerAddressType,
    paymentProfile,
    paymentType,
)
from authorizenet.apicontrollers import (
    createCustomerPaymentProfileController,
    createCustomerShippingAddressController,
)

from terminusgps_tracker.authorizenetapi.auth import get_merchant_auth


class TrackerSubscription(models.Model):
    class SubscriptionTier(models.TextChoices):
        COPPER = "Cu", _("Copper")
        SILVER = "Ag", _("Silver")
        GOLD = "Au", _("Gold")

    name = models.CharField(max_length=64)
    profile = models.ForeignKey(
        "TrackerProfile", on_delete=models.CASCADE, related_name="subscriptions"
    )
    tier = models.CharField(
        max_length=2, choices=SubscriptionTier.choices, default=SubscriptionTier.COPPER
    )
    amount = MoneyField(
        default=Money("0.00", "USD"),
        max_digits=15,
        decimal_places=2,
        default_currency="USD",
    )
    months = models.PositiveIntegerField(default=12)

    def __str__(self) -> str:
        return self.name

    def save(self, **kwargs) -> None:
        match self.tier:
            case self.SubscriptionTier.COPPER:
                rate = Money("19.99")
            case self.SubscriptionTier.SILVER:
                rate = Money("29.99")
            case self.SubscriptionTier.GOLD:
                rate = Money("39.99")
            case _:
                raise ValueError(f"Invalid tier: {self.tier}")
        self.amount = rate * self.months
        super().save(**kwargs)


class TrackerPaymentMethod(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    profile = models.ForeignKey(
        "TrackerProfile", on_delete=models.CASCADE, related_name="payments"
    )

    def __str__(self) -> str:
        return f"{self.profile.user.first_name}'s Payment Method"

    def save(
        self,
        payment: paymentType | None = None,
        billing_address: customerAddressType | None = None,
        default: bool = False,
        **kwargs,
    ) -> None:
        if payment is None or billing_address is None:
            return super().save(**kwargs)

        request = createCustomerPaymentProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(self.profile.authorizenet_profile_id),
            paymentProfile=paymentProfile(billTo=billing_address, payment=payment),
            defaultPaymentProfile=default,
        )
        controller = createCustomerPaymentProfileController(request)
        controller.execute()
        response: createCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode == "Ok":
            self.id = int(response.messages.customerPaymentProfileId)

        super().save(**kwargs)


class TrackerAddress(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    profile = models.ForeignKey(
        "TrackerProfile", on_delete=models.CASCADE, related_name="addresses"
    )

    def __str__(self) -> str:
        return f"{self.profile.user.first_name}'s Address"

    def save(
        self,
        shipping_address: customerAddressType | None = None,
        default: bool = False,
        **kwargs,
    ) -> None:
        if shipping_address is None:
            return super().save(**kwargs)

        request = createCustomerShippingAddressRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(self.profile.authorizenet_profile_id),
            address=shipping_address,
            defaultShippingAddress=default,
        )
        controller = createCustomerShippingAddressController(request)
        controller.execute()
        response: createCustomerShippingAddressResponse = controller.getresponse()
        if response.messages.resultCode == "Ok":
            self.id = int(response.messages.customerAddressId)

        super().save(**kwargs)
