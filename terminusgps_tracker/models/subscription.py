from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.money import Currency
from pyxb.binding.basis import element

from authorizenet.apicontrollers import (
    ARBCreateSubscriptionController,
    ARBCancelSubscriptionController,
    ARBGetSubscriptionStatusController,
)
from authorizenet.apicontractsv1 import (
    ARBCancelSubscriptionRequest,
    ARBCancelSubscriptionResponse,
    ARBCreateSubscriptionRequest,
    ARBCreateSubscriptionResponse,
    ARBGetSubscriptionStatusRequest,
    ARBGetSubscriptionStatusResponse,
    ARBSubscriptionType,
    ARBSubscriptionUnitEnum,
    customerProfileIdType,
    merchantAuthenticationType,
    paymentScheduleType,
    paymentScheduleTypeInterval,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.items import (
    WialonUnitGroup,
    WialonUser,
    WialonUnit,
)


class TrackerSubscriptionFeature(models.Model):
    class FeatureAmount(models.IntegerChoices):
        LOW = 5
        MID = 25
        INF = 999

    name = models.CharField(max_length=256)
    amount = models.IntegerField(
        choices=FeatureAmount.choices, default=None, null=True, blank=True
    )

    class Meta:
        verbose_name = "subscription feature"
        verbose_name_plural = "subscription features"

    def __str__(self) -> str:
        amount_display: str = self.get_amount_display()
        if amount_display:
            return mark_safe(amount_display + " " + self.name)
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
                return ""


class TrackerSubscriptionTier(models.Model):
    class IntervalPeriod(models.IntegerChoices):
        MONTHLY = 1
        QUARTERLY = 3
        ANNUALLY = 12

    class IntervalLength(models.IntegerChoices):
        HALF_YEAR = 6
        FULL_YEAR = 12

    name = models.CharField(max_length=256)
    unit_cmd = models.CharField(max_length=256, default=None, null=True, blank=True)
    group_id = models.PositiveBigIntegerField(default=None, null=True, blank=True)

    features = models.ManyToManyField("terminusgps_tracker.TrackerSubscriptionFeature")
    amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency=Currency("USD")
    )
    period = models.PositiveSmallIntegerField(
        choices=IntervalPeriod.choices, default=IntervalPeriod.MONTHLY
    )
    length = models.PositiveSmallIntegerField(
        choices=IntervalLength.choices, default=IntervalLength.FULL_YEAR
    )

    class Meta:
        verbose_name = "subscription tier"
        verbose_name_plural = "subscription tiers"

    def __str__(self) -> str:
        return self.name

    def save(self, **kwargs) -> None:
        if self.group_id is None:
            with WialonSession() as session:
                group_id: int = self.create_wialon_subscription_group(
                    27881459, session=session
                )
                self.group_id = group_id
        return super().save(**kwargs)

    def add_to_group(self, unit_id: str, session: WialonSession) -> None:
        if not self.group_id:
            raise ValueError(f"{self.name} has no Wialon group")

        group_id: str = str(self.group_id)
        unit = WialonUnit(id=unit_id, session=session)
        group = WialonUnitGroup(id=group_id, session=session)
        group.add_item(unit)

    def rm_from_group(self, unit_id: str, session: WialonSession) -> None:
        if not self.group_id:
            raise ValueError(f"{self.name} has no Wialon group")

        group_id: str = str(self.group_id)
        unit = WialonUnit(id=unit_id, session=session)
        group = WialonUnitGroup(id=group_id, session=session)
        group.rm_item(unit)

    def create_wialon_subscription_group(
        self, owner_id: int, session: WialonSession
    ) -> int:
        admin = WialonUser(id=str(owner_id), session=session)
        group = WialonUnitGroup(owner=admin, name=self.group_name, session=session)

        if not group or not group.id:
            raise ValueError("Failed to properly create Wialon subscription group")
        return group.id

    @property
    def group_name(self) -> str:
        return f"{self.name} Subscription Group"


class TrackerSubscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        SUSPENDED = "suspended", _("Suspended")
        CANCELED = "canceled", _("Canceled")
        TERMINATED = "terminated", _("Terminated")

    authorizenet_id = models.PositiveIntegerField(default=None, null=True, blank=True)
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    status = models.CharField(
        max_length=10,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.SUSPENDED,
    )
    tier = models.ForeignKey(
        "terminusgps_tracker.TrackerSubscriptionTier",
        on_delete=models.CASCADE,
        related_name="tier",
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
        if not self.authorizenet_id and self.tier is not None:
            request = self._generate_create_subscription_request(tier=self.tier)
            self.authorizenet_id = self.create_authorizenet_subscription(request)
        if self.authorizenet_id:
            self.refresh_status()
        return super().save(**kwargs)

    def delete(self, **kwargs):
        if self.authorizenet_id:
            merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
            subscriptionId: str = str(self.authorizenet_id)
            request = ARBCancelSubscriptionRequest(
                merchantAuthentication=merchantAuthentication,
                subscriptionId=subscriptionId,
            )

            self.cancel_authorizenet_subscription(request)
            self.refresh_status()
        return super().delete(**kwargs)

    def upgrade(self, new_tier: TrackerSubscriptionTier) -> None:
        if new_tier.amount < self.tier.amount:
            raise ValueError(f"Cannot upgrade to a lower tier than {self.tier}")

        request = self._generate_create_subscription_request(new_tier)
        self.authorizenet_id = self.create_authorizenet_subscription(request)
        self.tier = new_tier
        return self.refresh_status()

    def downgrade(self, new_tier: TrackerSubscriptionTier) -> None:
        if new_tier.amount > self.tier.amount:
            raise ValueError(f"Cannot downgrade to a higher tier than {self.tier}")

        request = self._generate_create_subscription_request(new_tier)
        self.authorizenet_id = self.create_authorizenet_subscription(request)
        self.tier = new_tier
        return self.refresh_status()

    def refresh_status(self) -> None:
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        subscriptionId = str(self.authorizenet_id)
        request = ARBGetSubscriptionStatusRequest(
            merchantAuthentication=merchantAuthentication, subscriptionId=subscriptionId
        )
        return self.refresh_authorizenet_subscription_status(request)

    def create_authorizenet_subscription(
        self, request: ARBCreateSubscriptionRequest
    ) -> int:
        controller = ARBCreateSubscriptionController(request)
        controller.execute()
        response: ARBCreateSubscriptionResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.subscriptionId)

    def cancel_authorizenet_subscription(
        self, request: ARBCancelSubscriptionRequest
    ) -> None:
        controller = ARBCancelSubscriptionController(request)
        controller.execute()
        response: ARBCancelSubscriptionResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    def refresh_authorizenet_subscription_status(
        self, request: ARBGetSubscriptionStatusRequest
    ) -> None:
        controller = ARBGetSubscriptionStatusController(request)
        controller.execute()
        response: ARBGetSubscriptionStatusResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        self.status = response.status

    def _generate_create_subscription_request(
        self, tier: TrackerSubscriptionTier, trialAmount: str = "0.00"
    ) -> element:
        name: str = f"{self.profile.fullName}'s {tier.name} Subscription"
        amount = str(tier.amount.amount)
        paymentSchedule: paymentScheduleType = self._generate_payment_schedule(tier)
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        profile: customerProfileIdType = customerProfileIdType(
            customerProfileId=self.profile.customerProfileId,
            customerPaymentProfileId=self.profile.customerPaymentProfileId,
            customerAddressId=self.profile.customerAddressId,
        )

        return ARBCreateSubscriptionRequest(
            merchantAuthentication=merchantAuthentication,
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
        trialOccurrences: str = str("0")
        interval: paymentScheduleTypeInterval = paymentScheduleTypeInterval(
            length=str(tier.length), unit=ARBSubscriptionUnitEnum.months
        )

        return paymentScheduleType(
            startDate=startDate,
            totalOccurrences=totalOccurrences,
            trialOccurrences=trialOccurrences,
            interval=interval,
        )
