from django.db import models
from django.utils import timezone
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Currency


from authorizenet.apicontractsv1 import (
    ARBCreateSubscriptionRequest,
    ARBCreateSubscriptionResponse,
    ARBSubscriptionType,
    ARBSubscriptionUnitEnum,
    customerProfileIdType,
    paymentScheduleType,
    paymentScheduleTypeInterval,
    subscriptionCustomerProfileType,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
from terminusgps_tracker.integrations.wialon.items.unit_group import WialonUnitGroup
from terminusgps_tracker.integrations.wialon.items.user import WialonUser
from terminusgps_tracker.integrations.wialon.items.unit import WialonUnit
from terminusgps_tracker.integrations.wialon.session import WialonSession


class TrackerSubscriptionFeature(models.Model):
    class FeatureAmount(models.IntegerChoices):
        LOW = 5
        MID = 25
        INF = 999

    name = models.CharField(max_length=256)
    amount = models.IntegerField(
        choices=FeatureAmount.choices, default=FeatureAmount.LOW
    )

    class Meta:
        verbose_name = "subscription feature"
        verbose_name_plural = "subscription features"

    def __str__(self) -> str:
        if self.amount:
            amount_display: str = self.get_amount_display()
            return mark_safe(f"{amount_display} {self.name}")
        return self.name

    def get_amount_display(self) -> str:
        match self.amount:
            case TrackerSubscriptionFeature.FeatureAmount.LOW:  # 5
                return str(TrackerSubscriptionFeature.FeatureAmount.LOW)
            case TrackerSubscriptionFeature.FeatureAmount.MID:  # 25
                return str(TrackerSubscriptionFeature.FeatureAmount.MID)
            case TrackerSubscriptionFeature.FeatureAmount.INF:  # 999
                return "&#8734;"  # Infinity symbol
            case _:
                return "?"


class TrackerSubscriptionTier(models.Model):
    class IntervalPeriod(models.IntegerChoices):
        MONTHLY = 1
        QUARTERLY = 3
        ANNUALLY = 12

    class IntervalLength(models.IntegerChoices):
        HALF_YEAR = 6
        FULL_YEAR = 12

    name = models.CharField(max_length=256)
    period = models.PositiveSmallIntegerField(
        choices=IntervalPeriod.choices, default=IntervalPeriod.MONTHLY
    )
    length = models.PositiveSmallIntegerField(
        choices=IntervalLength.choices, default=IntervalLength.FULL_YEAR
    )
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency=Currency("USD")
    )
    features = models.ManyToManyField("terminusgps_tracker.TrackerSubscriptionFeature")

    unit_cmd = models.CharField(max_length=256, default=None, null=True, blank=True)
    wialon_group_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )

    class Meta:
        verbose_name = "subscription tier"
        verbose_name_plural = "subscription tiers"

    def __str__(self) -> str:
        return self.name

    def save(self, **kwargs) -> None:
        if not self.wialon_group_id:
            self.wialon_group_id = self._create_wialon_subscription_group()
        return super().save(**kwargs)

    def delete(self, **kwargs):
        if self.wialon_group_id:
            with WialonSession() as session:
                WialonUnitGroup(id=str(self.wialon_group_id), session=session).delete()
        return super().delete(**kwargs)

    def add_to_group(self, unit_id: str) -> None:
        if not self.wialon_group_id:
            raise ValueError(f"{self.name} has no Wialon group")

        group_id: str = str(self.wialon_group_id)
        with WialonSession() as session:
            unit = WialonUnit(id=unit_id, session=session)
            group = WialonUnitGroup(id=group_id, session=session)
            group.add_item(unit)

    def rm_from_group(self, unit_id: str) -> None:
        if not self.wialon_group_id:
            raise ValueError(f"{self.name} has no Wialon group")

        group_id: str = str(self.wialon_group_id)
        with WialonSession() as session:
            unit = WialonUnit(id=unit_id, session=session)
            group = WialonUnitGroup(id=group_id, session=session)
            group.rm_item(unit)

    def _create_wialon_subscription_group(
        self, admin_user_id: int | None = 27881459
    ) -> int | None:
        with WialonSession() as session:
            admin_user = WialonUser(id=str(admin_user_id), session=session)
            unit_group = WialonUnitGroup(
                owner=admin_user,
                name=f"{self.name} Subscription Group",
                session=session,
            )
            return unit_group.id


class TrackerSubscription(models.Model):
    authorizenet_id = models.PositiveIntegerField(default=None, null=True, blank=True)

    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="subscription",
        primary_key=True,
    )
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

    class Meta:
        verbose_name = "subscription"
        verbose_name_plural = "subscriptions"

    def __str__(self) -> str:
        return str(self.profile)

    def save(self, **kwargs) -> None:
        if self.curr_tier != self.prev_tier:
            request = self._generate_create_subscription_request(tier=self.curr_tier)
            controller = ARBCreateSubscriptionController(request)
            controller.execute()
            response: ARBCreateSubscriptionResponse = controller.getresponse()
            if response.messages.resultCode != "Ok":
                raise ValueError(response.messages.message["text"].text)
            self.authorizenet_id = int(response.subscriptionId)
            self.prev_tier = self.curr_tier
        return super().save(**kwargs)

    def _generate_create_subscription_request(
        self, tier: TrackerSubscriptionTier
    ) -> ARBCreateSubscriptionRequest:
        name: str = f"{self.profile.fullName}'s {tier.name} Subscription"
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
            subscription=ARBSubscriptionType(
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
        if tier.length < tier.period:
            raise ValueError(
                f"Invalid length-period combination: {tier.length} is less than {tier.period}"
            )

        startDate: str = f"{timezone.now():%Y-%m-%d}"
        totalOccurrences: str = str(tier.length // int(tier.period))
        trialOccurrences: str = str(0.00)
        interval: paymentScheduleTypeInterval = paymentScheduleTypeInterval(
            length=str(tier.length), unit=ARBSubscriptionUnitEnum.months
        )

        return paymentScheduleType(
            startDate=startDate,
            totalOccurrences=totalOccurrences,
            trialOccurrences=trialOccurrences,
            interval=interval,
        )
