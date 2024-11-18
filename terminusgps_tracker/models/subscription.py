from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from djmoney.money import Money, Currency
from djmoney.models.fields import MoneyField

from authorizenet.apicontractsv1 import (
    ARBSubscriptionUnitEnum,
    customerProfileType,
    paymentScheduleType,
    paymentScheduleTypeInterval,
    subscriptionPaymentType,
)


class TrackerSubscription(models.Model):
    class SubscriptionTier(models.TextChoices):
        COPPER = "Cu", _("Copper")
        SILVER = "Ag", _("Silver")
        GOLD = "Au", _("Gold")

    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128)
    tier = models.CharField(
        max_length=2, choices=SubscriptionTier.choices, default=SubscriptionTier.COPPER
    )
    duration = models.PositiveIntegerField(default=12)
    start_date = models.DateField(default=timezone.now)
    rate = MoneyField(max_digits=14, decimal_places=2, default_currency=Currency("USD"))

    has_trial_month = models.BooleanField(default=False)
    gradient = models.CharField(
        max_length=128,
        default="from-terminus-gray-500 to-terminus-gray-500 via-terminus-gray-500",
    )

    def __str__(self) -> str:
        return self.name

    def __len__(self) -> int:
        return self.duration

    @property
    def tier_display_gradient(self) -> str:
        return mark_safe(
            f'<span class="font-bold bg-gradient-to-br bg-clip-text text-transparent {self.gradient}">{self.get_tier_display()}</span>'
        )

    def save(self, **kwargs) -> None:
        match self.tier:
            case self.SubscriptionTier.COPPER:
                self.rate = Money(Decimal("19.99"), currency=Currency("USD"))
                self.gradient = "from-orange-700 to-orange-700 via-orange-300"
            case self.SubscriptionTier.SILVER:
                self.rate = Money(Decimal("29.99"), currency=Currency("USD"))
                self.gradient = "from-gray-700 to-gray-700 via-gray-300"
            case self.SubscriptionTier.GOLD:
                self.rate = Money(Decimal("39.99"), currency=Currency("USD"))
                self.gradient = "from-yellow-700 to-yellow-700 via-yellow-300"
        super().save(**kwargs)
