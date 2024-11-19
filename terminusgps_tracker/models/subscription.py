from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _
from djmoney.money import Money, Currency
from djmoney.models.fields import MoneyField


from authorizenet.apicontractsv1 import (
    ARBCreateSubscriptionRequest,
    ARBCreateSubscriptionResponse,
    ARBSubscriptionType,
    ARBSubscriptionUnitEnum,
    customerProfileIdType,
    customerProfileType,
    merchantAuthenticationType,
    paymentScheduleType,
    paymentScheduleTypeInterval,
    subscriptionCustomerProfileType,
    subscriptionPaymentType,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
from terminusgps_tracker.forms.subscriptions import SubscriptionCreationForm
from terminusgps_tracker.integrations.wialon.items import unit_group
from terminusgps_tracker.integrations.wialon.session import WialonSession


class TrackerSubscriptionTier(models.Model):
    class IntervalPeriod(models.TextChoices):
        MONTHLY = "1", _("Monthly")
        QUARTERLY = "3", _("Quarterly")
        ANNUALLY = "12", _("Annually")

    name = models.CharField(max_length=128)
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency=Currency("USD")
    )
    period = models.CharField(
        max_length=2, choices=IntervalPeriod.choices, default=IntervalPeriod.MONTHLY
    )
    length = models.PositiveIntegerField(
        choices=((1, _("One year")), (2, _("Two years"))), default=1
    )
    wialon_group_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name

    def save(self, **kwargs) -> None:
        return super().save(**kwargs)


class TrackerSubscription(models.Model):
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="subscription",
        primary_key=True,
    )
    authorizenet_id = models.PositiveIntegerField(default=None, null=True, blank=True)
    curr_tier = models.ForeignKey(
        "terminusgps_tracker.TrackerSubscriptionTier",
        related_name="current_tier",
        verbose_name="current_tier",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
    )
    prev_tier = models.ForeignKey(
        "terminusgps_tracker.TrackerSubscriptionTier",
        related_name="previous_tier",
        verbose_name="previous_tier",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.profile)

    def save(self, **kwargs) -> None:
        if self.tier != self.prev_tier:
            request = self._generate_create_subscription_request(tier=self.tier)
            controller = ARBCreateSubscriptionController(request)
            controller.execute()
            response: ARBCreateSubscriptionResponse = controller.getresponse()
            if response.messages.resultCode != "Ok":
                raise ValueError(response.messages.message["text"].text)
            self.authorizenet_id = int(response.subscriptionId)
            self.prev_tier = self.tier
        return super().save(**kwargs)

    def _get_create_subscription_request(
        self, tier: TrackerSubscriptionTier
    ) -> ARBCreateSubscriptionRequest:
        name: str = f"{self.profile.user.username}'s {tier.name} Subscription"
        amount = str(tier.amount)
        trialAmount = str("0.00")
        paymentSchedule: paymentScheduleType = self._generate_payment_schedule(
            tier=tier
        )
        profile: customerProfileIdType = customerProfileIdType(
            customerProfileId=self.profile.customerProfileId,
            customerPaymentProfileId=self.profile.customerPaymentProfileId,
            customerAddressId=self.profile.customerAddressId,
        )

        return ARBCreateSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscription=subscriptionCustomerProfileType(
                name=name,
                paymentSchedule=paymentSchedule,
                amount=amount,
                trialAmount=trialAmount,
                profile=profile,
            ),
        )

    def _generate_payment_schedule(
        self, tier: TrackerSubscriptionTier
    ) -> paymentScheduleType:
        startDate: str = f"{timezone.now():%Y-%m-%d}"
        totalOccurances: str = str(tier.length * int(tier.period))
        trialOccurances: str = "0"
        interval: paymentScheduleTypeInterval = paymentScheduleTypeInterval(
            length=str(tier.length), unit=ARBSubscriptionUnitEnum.months
        )

        return paymentScheduleType(
            startDate=startDate,
            interval=interval,
            totalOccurances=totalOccurances,
            trialOccurances=trialOccurances,
        )
