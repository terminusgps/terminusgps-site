from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from djmoney.money import Money, Currency

from authorizenet.apicontractsv1 import (
    ARBSubscriptionUnitEnum,
    createCustomerPaymentProfileRequest,
    createCustomerPaymentProfileResponse,
    createCustomerShippingAddressRequest,
    createCustomerShippingAddressResponse,
    customerAddressType,
    customerProfileType,
    paymentProfile,
    paymentScheduleType,
    paymentScheduleTypeInterval,
    paymentType,
    subscriptionPaymentType,
)
from authorizenet.apicontrollers import (
    createCustomerPaymentProfileController,
    createCustomerShippingAddressController,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth


class TrackerSubscription(models.Model):
    class SubscriptionTier(models.TextChoices):
        COPPER = "Cu", _("Copper")
        SILVER = "Ag", _("Silver")
        GOLD = "Au", _("Gold")

    tier = models.CharField(
        max_length=2, choices=SubscriptionTier.choices, default=SubscriptionTier.COPPER
    )
    months = models.PositiveIntegerField(default=12)
    start_date = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.pk}-{self.tier} Subscription"

    def __len__(self) -> int:
        return self.months

    @classmethod
    def get_rate(cls, tier: SubscriptionTier) -> Money:
        match tier:
            case cls.SubscriptionTier.COPPER:
                return Money(Decimal("19.99"), Currency("USD"))
            case cls.SubscriptionTier.SILVER:
                return Money(Decimal("29.99"), Currency("USD"))
            case cls.SubscriptionTier.GOLD:
                return Money(Decimal("39.99"), Currency("USD"))

    @property
    def paymentSchedule(self) -> paymentScheduleType:
        return paymentScheduleType(
            interval=paymentScheduleTypeInterval(
                length=str(1), unit=ARBSubscriptionUnitEnum.months
            ),
            startDate=f"{self.start_date:%Y-%m-%d}",
            totalOccurrences=str(len(self)),
        )

    @property
    def amount(self) -> Money:
        rate = TrackerSubscription.get_rate(tier=self.tier)
        return rate * Decimal(str(self.months))

    @property
    def subscriptionPaymentType(self) -> subscriptionPaymentType:
        return subscriptionPaymentType(
            name=self.get_tier_display(),
            paymentSchedule=self.paymentSchedule,
            amount=str(self.amount),
            profile=customerProfileType(
                customerProfileId=str(self.profile.authorizenet_profile_id),
                customerPaymentProfileId=str(
                    self.profile.payments.filter(default__exact=True).first()
                ),
            ),
        )


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
            customerProfileId=str(self.profile.customerProfileId),
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
