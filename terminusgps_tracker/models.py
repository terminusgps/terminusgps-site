from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from authorizenet.apicontractsv1 import deleteCustomerProfileRequest
from authorizenet.apicontrollers import deleteCustomerProfileController

from terminusgps_tracker.authorizenetapi.auth import get_merchant_auth
from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items import (
    WialonUser,
    WialonUnitGroup,
    WialonResource,
)


class CustomerPaymentProfile(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    is_default = models.BooleanField(default=False)
    profile = models.ForeignKey(
        "CustomerProfile", on_delete=models.CASCADE, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"Payment profile #{self.id}"


class CustomerAddress(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    is_default = models.BooleanField(default=False)
    profile = models.ForeignKey(
        "CustomerProfile", on_delete=models.CASCADE, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"Address #{self.id}"


class CustomerProfile(models.Model):
    class SubscriptionTier(models.TextChoices):
        COPPER = "Cu", _("Copper tier")
        SILVER = "Ag", _("Silver tier")
        GOLD = "Au", _("Gold tier")
        PLATINUM = "Pt", _("Platinum tier")

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    subscription_tier = models.CharField(
        max_length=2, choices=SubscriptionTier.choices, default=SubscriptionTier.COPPER
    )
    payments = models.ManyToManyField(CustomerPaymentProfile, default=None)
    addresses = models.ManyToManyField(CustomerAddress, default=None)

    authorizenet_profile_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_super_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_group_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )
    wialon_resource_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"

    def delete(self, *args, **kwargs):
        self._delete_authorizenet_objects()
        self._delete_wialon_objects()
        return super().delete(*args, **kwargs)

    def _delete_authorizenet_objects(self) -> None:
        if self.authorizenet_profile_id is not None:
            request = deleteCustomerProfileRequest(
                merchantAuthentication=get_merchant_auth(),
                customerProfileId=str(self.authorizenet_profile_id),
            )
            controller = deleteCustomerProfileController(request)
            controller.execute()

    def _delete_wialon_objects(self) -> None:
        if all(
            [
                self.wialon_super_user_id,
                self.wialon_user_id,
                self.wialon_resource_id,
                self.wialon_group_id,
            ]
        ):
            with WialonSession() as session:
                super_user = WialonUser(
                    id=str(self.wialon_super_user_id), session=session
                )
                user = WialonUser(id=str(self.wialon_user_id), session=session)
                group = WialonUnitGroup(id=str(self.wialon_group_id), session=session)
                resource = WialonResource(
                    id=str(self.wialon_resource_id), session=session
                )
                user.delete()
                group.delete()
                resource.delete()
                super_user.delete()

    @property
    def merchantCustomerId(self) -> str:
        return str(self.user.pk)
