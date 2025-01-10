from typing import Any
from decimal import Decimal

from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.auth import get_merchant_auth, get_environment
from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.items import WialonUnitGroup, WialonUnit

from authorizenet.apicontrollers import (
    ARBCreateSubscriptionController,
    ARBCancelSubscriptionController,
    ARBGetSubscriptionController,
    ARBGetSubscriptionStatusController,
    ARBUpdateSubscriptionController,
)
from authorizenet.apicontractsv1 import (
    ARBCancelSubscriptionRequest,
    ARBCreateSubscriptionRequest,
    ARBGetSubscriptionRequest,
    ARBGetSubscriptionStatusRequest,
    ARBSubscriptionType,
    ARBSubscriptionUnitEnum,
    ARBUpdateSubscriptionRequest,
    customerProfileIdType,
    paymentScheduleType,
    paymentScheduleTypeInterval,
)


class TrackerSubscriptionFeature(models.Model):
    name = models.CharField(max_length=256)
    desc = models.CharField(max_length=2048, default=None, null=True, blank=True)

    class Meta:
        verbose_name = "subscription feature"
        verbose_name_plural = "subscription features"

    def __str__(self) -> str:
        return self.name


class TrackerSubscriptionTier(models.Model):
    class IntervalPeriod(models.IntegerChoices):
        MONTHLY = 1
        QUARTERLY = 3
        ANNUALLY = 12

    class IntervalLength(models.IntegerChoices):
        HALF_YEAR = 6
        FULL_YEAR = 12

    name = models.CharField(max_length=256)
    wialon_id = models.PositiveBigIntegerField(default=None, null=True, blank=True)
    wialon_cmd = models.CharField(max_length=256, default=None, null=True, blank=True)

    features = models.ManyToManyField("terminusgps_tracker.TrackerSubscriptionFeature")
    amount = models.DecimalField(default=0.00, max_digits=14, decimal_places=2)
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

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        if not self.wialon_id and session is not None:
            self.wialon_id = self.wialon_create_group(
                name=f"{self.name} Subscription Group", session=session
            )
        return super().save(**kwargs)

    def wialon_add_to_group(self, unit_id: int, session: WialonSession) -> None:
        assert self.wialon_id
        unit = WialonUnit(id=str(unit_id), session=session)
        group = WialonUnitGroup(id=str(self.wialon_id), session=session)
        group.add_item(unit)

    def wialon_rm_from_group(self, unit_id: int, session: WialonSession) -> None:
        assert self.wialon_id
        unit = WialonUnit(id=str(unit_id), session=session)
        group = WialonUnitGroup(id=str(self.wialon_id), session=session)
        group.rm_item(unit)

    def wialon_execute_subscription_command(
        self, unit_id: int, session: WialonSession, timeout: int = 5
    ) -> None:
        session.wialon_api.unit_exec_cmd(
            **{
                "itemId": unit_id,
                "commandName": self.name,
                "linkType": "",
                "timeout": timeout,
                "flags": 0,
            }
        )

    @staticmethod
    def wialon_create_group(name: str, session: WialonSession) -> int:
        response: dict = session.wialon_api.core_create_unit_group(
            **{
                "creatorId": settings.WIALON_ADMIN_ID,
                "name": name,
                "dataFlags": flags.DATAFLAG_UNIT_BASE,
            }
        )
        return int(response["item"].get("id"))


class TrackerSubscription(models.Model):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        SUSPENDED = "suspended", _("Suspended")
        CANCELED = "canceled", _("Canceled")
        TERMINATED = "terminated", _("Terminated")

    authorizenet_id = models.PositiveIntegerField(default=None, null=True, blank=True)
    payment_id = models.PositiveIntegerField(default=None, null=True, blank=True)
    address_id = models.PositiveIntegerField(default=None, null=True, blank=True)
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

    @transaction.atomic
    def upgrade(
        self,
        new_tier: TrackerSubscriptionTier,
        payment_id: int | None = None,
        address_id: int | None = None,
    ) -> None:
        assert payment_id or self.payment_id, "No payment method found."
        assert address_id or self.address_id, "No shipping method found."

        if self.tier is None or self.authorizenet_id is None:
            self.authorizenet_id = self.authorizenet_create_subscription(
                new_tier, payment_id or self.payment_id, address_id or self.payment_id
            )
        elif self.tier and new_tier.amount < self.tier.amount:
            raise ValueError("Cannot upgrade to a lower tier.")
        else:
            self.authorizenet_update_subscription(
                new_tier, payment_id or self.payment_id, address_id or self.payment_id
            )

        self.tier = new_tier
        self.payment_id = payment_id
        self.address_id = address_id
        self.refresh_status()

    @transaction.atomic
    def downgrade(
        self,
        new_tier: TrackerSubscriptionTier,
        payment_id: int | None = None,
        address_id: int | None = None,
    ) -> None:
        assert payment_id or self.payment_id, "No payment method found."
        assert address_id or self.address_id, "No shipping method found."

        if self.tier is None or self.authorizenet_id is None:
            self.authorizenet_id = self.authorizenet_create_subscription(
                new_tier, payment_id or self.payment_id, address_id or self.address_id
            )
        elif self.tier and new_tier.amount > self.tier.amount:
            raise ValueError("Cannot downgrade to a higher tier.")
        else:
            self.authorizenet_update_subscription(
                new_tier, payment_id or self.payment_id, address_id or self.address_id
            )

        self.tier = new_tier
        self.payment_id = payment_id
        self.address_id = address_id
        self.refresh_status()

    @transaction.atomic
    def refresh_status(self) -> None:
        assert self.authorizenet_id, "No subscription to refresh status"
        self.status = self.authorizenet_get_subscription_status(self.authorizenet_id)

    @transaction.atomic
    def cancel(self) -> None:
        assert self.authorizenet_id, "No subscription to cancel"
        self.authorizenet_cancel_subscription(self.authorizenet_id)
        self.refresh_status()

    @classmethod
    def authorizenet_get_subscription_status(cls, subscription_id: int) -> str:
        request = ARBGetSubscriptionStatusRequest(
            merchantAuthentication=get_merchant_auth(),
            subscriptionId=str(subscription_id),
        )

        controller = ARBGetSubscriptionStatusController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

        return str(response.status)

    @classmethod
    def authorizenet_get_subscription(
        cls, subscription_id: int, includeTransactions: bool = False
    ) -> dict[str, Any]:
        request = ARBGetSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscriptionId=str(subscription_id),
            includeTransactions=includeTransactions,
        )

        controller = ARBGetSubscriptionController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

        return {
            "subscription": {
                "name": response.subscription.name,
                "paymentSchedule": {
                    "intervalLength": response.subscription.paymentSchedule.interval.length,
                    "intervalUnit": response.subscription.paymentSchedule.interval.unit,
                    "startDate": response.subscription.paymentSchedule.startDate,
                    "totalOccurrences": response.subscription.paymentSchedule.totalOccurrences,
                    "trialOccurrences": response.subscription.paymentSchedule.trialOccurrences,
                },
                "amount": response.subscription.amount,
                "trialAmount": response.subscription.trialAmount,
                "status": response.subscription.status,
                "arbTransactions": response.arbTransactions,
            }
        }

    @classmethod
    def authorizenet_cancel_subscription(cls, subscription_id: int) -> None:
        request = ARBCancelSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscriptionId=str(subscription_id),
        )

        controller = ARBCancelSubscriptionController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    def authorizenet_update_subscription(
        self,
        tier: TrackerSubscriptionTier,
        payment_id: int,
        address_id: int,
        trial_amount: str | None = None,
    ) -> None:
        request = ARBUpdateSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscription=self.generate_customer_subscription(
                tier, payment_id, address_id, trial_amount
            ),
        )

        controller = ARBUpdateSubscriptionController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    def authorizenet_create_subscription(
        self, tier: TrackerSubscriptionTier, payment_id: int, address_id: int
    ) -> int:
        request = ARBCreateSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscription=self.generate_customer_subscription(
                tier, payment_id, address_id
            ),
        )

        controller = ARBCreateSubscriptionController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.subscriptionId)

    def generate_customer_subscription(
        self,
        tier: TrackerSubscriptionTier,
        payment_id: int,
        address_id: int,
        trial_amount: str | None = None,
    ) -> ARBSubscriptionType:
        paymentSchedule: paymentScheduleType = self.generate_payment_schedule(tier)
        profile: customerProfileIdType = self.generate_customer_profile(
            payment_id, address_id
        )

        return ARBSubscriptionType(
            name=f"{self.profile.user.email}'s {tier} Subscription",
            paymentSchedule=paymentSchedule,
            amount=str(tier.amount),
            trialAmount=trial_amount if trial_amount else str("0.00"),
            profile=profile,
        )

    def generate_customer_profile(
        self, payment_id: int, address_id: int
    ) -> customerProfileIdType:
        assert self.profile.authorizenet_id
        return customerProfileIdType(
            customerProfileId=str(self.profile.authorizenet_id),
            customerPaymentProfileId=str(payment_id),
            customerAddressId=str(address_id),
        )

    @classmethod
    def generate_payment_schedule(
        cls, tier: TrackerSubscriptionTier, trial_occurrences: int = 0
    ) -> paymentScheduleType:
        if tier.length < tier.period:
            raise ValueError("Tier length cannot be less than tier period")

        startDate: str = f"{timezone.now():%Y-%m-%d}"
        totalOccurrences: str = str(tier.length // int(tier.period))
        trialOccurrences: str = str(trial_occurrences)
        interval: paymentScheduleTypeInterval = paymentScheduleTypeInterval(
            length=str(tier.length), unit=ARBSubscriptionUnitEnum.months
        )

        return paymentScheduleType(
            startDate=startDate,
            totalOccurrences=totalOccurrences,
            trialOccurrences=trialOccurrences,
            interval=interval,
        )

    @property
    def remaining_amount(self) -> Decimal:
        return Decimal()
