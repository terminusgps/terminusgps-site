from typing import Any
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
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

    class WialonCommandType(models.TextChoices):
        ENGINE_BLOCK = "block_engine", _("Block engine")
        ENGINE_UNBLOCK = "unblock_engine", _("Unblock engine")
        MSG_CUSTOM = "custom_msg", _("Custom message")
        MSG_DRIVER = "driver_msg", _("Message to driver")
        MSG_DOWNLOAD = "download_msgs", _("Download messages")
        QUERY_POS = "query_pos", _("Query position")
        QUERY_PHOTO = "query_photo", _("Query snapshot")
        OUTPUT_ON = "output_on", _("Activate output")
        OUTPUT_OFF = "output_off", _("Deactivate output")
        SEND_POS = "send_position", _("Send coordinates")
        SET_REPORT_INT = "set_report_interval", _("Set data transfer interval")
        UPLOAD_CFG = "upload_cfg", _("Upload configuration")
        UPLOAD_SW = "upload_sw", _("Upload firmware")

    class WialonCommandLink(models.TextChoices):
        AUTO = "", _("Automatic link")
        TCP = "tcp", _("TCP")
        UDP = "udp", _("UDP")
        VRT = "vrt", _("Virtual")
        GSM = "gsm", _("SMS")

    name = models.CharField(max_length=256)
    wialon_id = models.PositiveBigIntegerField(default=None, null=True, blank=True)
    wialon_cmd = models.CharField(max_length=256, default=None, null=True, blank=True)
    wialon_cmd_link = models.CharField(
        max_length=3,
        choices=WialonCommandLink.choices,
        default=WialonCommandLink.AUTO,
        blank=True,
    )
    wialon_cmd_type = models.CharField(
        max_length=32,
        choices=WialonCommandType.choices,
        default=WialonCommandType.UPLOAD_CFG,
    )

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

    def save(self, **kwargs) -> None:
        with WialonSession() as session:
            if self.wialon_id is None:
                admin_id: int = settings.WIALON_ADMIN_ID
                self.wialon_id: int = self.wialon_create_subscription_group(
                    owner_id=admin_id, session=session
                )
            self.wialon_execute_subscription_command(session=session, timeout=5)
        return super().save(**kwargs)

    def wialon_add_to_group(self, unit_id: int, session: WialonSession) -> None:
        if not self.wialon_id:
            raise ValueError(f"{self.name} has no Wialon group")

        group_id: int = self.wialon_id
        unit: WialonUnit = WialonUnit(id=str(unit_id), session=session)
        group: WialonUnitGroup = WialonUnitGroup(id=str(group_id), session=session)
        group.add_item(unit)

    def wialon_rm_from_group(self, unit_id: int, session: WialonSession) -> None:
        if not self.wialon_id:
            raise ValueError(f"{self.name} has no Wialon group")

        group_id: int = self.wialon_id
        unit: WialonUnit = WialonUnit(id=str(unit_id), session=session)
        group: WialonUnitGroup = WialonUnitGroup(id=str(group_id), session=session)
        group.rm_item(unit)

    def wialon_create_subscription_group(
        self, owner_id: int, session: WialonSession
    ) -> int:
        admin = WialonUser(id=str(owner_id), session=session)
        group = WialonUnitGroup(owner=admin, name=self.group_name, session=session)

        if not group or not group.id:
            raise ValueError("Failed to properly create Wialon subscription group")
        return group.id

    def wialon_execute_subscription_command(
        self, session: WialonSession, timeout: int = 5
    ) -> None:
        group = WialonUnitGroup(id=str(self.wialon_id), session=session)
        for unit_id in group.items:
            session.wialon_api.unit_exec_cmd(
                **{
                    "itemId": str(unit_id),
                    "commandName": self.wialon_cmd,
                    "linkType": self.wialon_cmd_link,
                    "param": {},
                    "timeout": timeout,
                    "flags": 0,
                }
            )

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

    def update_tier(
        self,
        new_tier: TrackerSubscriptionTier,
        payment_id: int | None = None,
        address_id: int | None = None,
    ) -> None:
        self.tier = new_tier
        self.authorizenet_id = self.authorizenet_update_subscription(
            new_tier, payment_id, address_id
        )

    def refresh_status(self) -> None:
        self.status = self.authorizenet_get_subscription_status(
            ARBGetSubscriptionStatusRequest(
                merchantAuthentication=get_merchant_auth(),
                subscriptionId=str(self.authorizenet_id),
            )
        )

    @classmethod
    def authorizenet_get_subscription_status(cls, subscription_id: int) -> str:
        request = ARBGetSubscriptionStatusRequest(
            merchantAuthentication=get_merchant_auth(),
            subscriptionId=str(subscription_id),
        )

        controller = ARBGetSubscriptionStatusController(request)
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
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    def authorizenet_update_subscription(
        self,
        tier: TrackerSubscriptionTier,
        payment_id: int | None = None,
        address_id: int | None = None,
    ) -> None:
        request = ARBUpdateSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscription=self.generate_customer_subscription(
                tier, payment_id, address_id
            ),
        )

        controller = ARBUpdateSubscriptionController(request)
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    def authorizenet_create_subscription(
        self,
        tier: TrackerSubscriptionTier,
        payment_id: int | None = None,
        address_id: int | None = None,
    ) -> int:
        request = ARBCreateSubscriptionRequest(
            merchantAuthentication=get_merchant_auth(),
            subscription=self.generate_customer_subscription(
                tier, payment_id, address_id
            ),
        )

        controller = ARBCreateSubscriptionController(request)
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.subscriptionId)

    def generate_customer_subscription(
        self,
        tier: TrackerSubscriptionTier,
        payment_id: int | None = None,
        address_id: int | None = None,
    ) -> ARBSubscriptionType:
        paymentSchedule: paymentScheduleType = self.generate_payment_schedule(tier)
        profile: customerProfileIdType = self.generate_customer_profile(
            payment_id, address_id
        )

        return ARBSubscriptionType(
            name=f"{self.profile.user.email}'s {tier} Subscription",
            paymentSchedule=paymentSchedule,
            amount=str(tier.amount),
            trialAmount=str("0.00"),
            profile=profile,
        )

    def generate_customer_profile(
        self, payment_id: int | None = None, address_id: int | None = None
    ) -> customerProfileIdType:
        if self.profile.authorizenet_id is None:
            raise ValueError(
                "Subscription profile requires an Authorizenet customer profile"
            )

        payment_id: int = payment_id if payment_id else self.payment_id
        address_id: int = address_id if address_id else self.address_id

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
            raise ValueError(
                f"Invalid length-period combination: {tier.length} is less than {tier.period}"
            )

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
    def payment_id(self) -> int:
        return (
            self.profile.payments.filter()
            .order_by("-is_default")
            .first()
            .authorizenet_id
        )

    @property
    def address_id(self) -> int:
        return (
            self.profile.addresses.filter()
            .order_by("-is_default")
            .first()
            .authorizenet_id
        )
