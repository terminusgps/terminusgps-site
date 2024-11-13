from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from djmoney.money import Money, Currency

from authorizenet.apicontractsv1 import (
    ARBSubscriptionUnitEnum,
    customerProfileType,
    paymentScheduleType,
    paymentScheduleTypeInterval,
    subscriptionPaymentType,
)

from terminusgps_tracker.models import TrackerProfile


class TrackerSubscription(models.Model):
    class SubscriptionTier(models.TextChoices):
        COPPER = "Cu", _("Copper")
        SILVER = "Ag", _("Silver")
        GOLD = "Au", _("Gold")

    name = models.CharField(max_length=128)
    tier = models.CharField(
        max_length=2, choices=SubscriptionTier.choices, default=SubscriptionTier.COPPER
    )
    duration = models.PositiveIntegerField(default=12)
    start_date = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return self.name

    def __len__(self) -> int:
        return self.duration

    @property
    def rate(self) -> Money:
        match self.tier:
            case self.SubscriptionTier.COPPER:
                return Money(Decimal("19.99"), Currency("USD"))
            case self.SubscriptionTier.SILVER:
                return Money(Decimal("29.99"), Currency("USD"))
            case self.SubscriptionTier.GOLD:
                return Money(Decimal("39.99"), Currency("USD"))
            case _:
                raise ValueError(f"Invalid tier: {self.tier}")

    @property
    def tier_gradient(self) -> str:
        match self.tier:
            case TrackerSubscription.SubscriptionTier.COPPER:
                return "from-orange-600 via-orange-400 to-orange-600"
            case TrackerSubscription.SubscriptionTier.SILVER:
                return "from-gray-600 via-gray-400 to-gray-600"
            case TrackerSubscription.SubscriptionTier.GOLD:
                return "from-yellow-600 via-yellow-400 to-yellow-600"
            case _:
                return ""

    @property
    def tier_display(self) -> str:
        return mark_safe(
            f'<span class="font-bold bg-gradient-to-br bg-clip-text text-transparent {self.tier_gradient}">{self.get_tier_display()}</span>'
        )

    @property
    def paymentSchedule(self) -> paymentScheduleType:
        return self.generate_payment_schedule()

    def generate_payment_schedule(self, period: int = 1) -> paymentScheduleType:
        return paymentScheduleType(
            interval=paymentScheduleTypeInterval(
                length=str(period), unit=ARBSubscriptionUnitEnum.months
            ),
            startDate=f"{self.start_date:%Y-%m-%d}",
        )

    def generate_subscription_payment(
        self, profile: TrackerProfile
    ) -> subscriptionPaymentType:
        return subscriptionPaymentType(
            name=self.name,
            paymentSchedule=self.paymentSchedule,
            amount=self.rate,
            profile=customerProfileType(
                customerProfileId=str(profile.authorizenet_profile_id)
            ),
        )
