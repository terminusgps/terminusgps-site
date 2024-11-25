from django.contrib.auth import get_user_model
from django.db import models

from authorizenet.apicontractsv1 import (
    customerProfileType,
    merchantAuthenticationType,
    createCustomerProfileRequest,
    createCustomerProfileResponse,
    deleteCustomerProfileRequest,
    deleteCustomerProfileResponse,
)
from authorizenet.apicontrollers import (
    createCustomerProfileController,
    deleteCustomerProfileController,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.items import (
    WialonUser,
    WialonUnitGroup,
    WialonResource,
)


class TrackerWialonProfile(models.Model):
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="wialon_profile",
    )
    user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    super_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    group_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )
    resource_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"{self.profile.user}'s Wialon Profile"

    def save(self, **kwargs) -> None:
        with WialonSession() as session:
            admin = WialonUser(id="27881459", session=session)
            if self.super_user_id:
                super_user = WialonUser(id=str(self.super_user_id), session=session)
            else:
                super_user = WialonUser(
                    owner=admin,
                    name=f"super_{self.profile.user.username}",
                    session=session,
                )
                self.super_user_id = super_user.id

            if not self.user_id:
                end_user = WialonUser(
                    owner=super_user, name=self.profile.user.username, session=session
                )
                self.user_id = end_user.id

            if not self.group_id:
                group = WialonUnitGroup(
                    owner=super_user,
                    name=f"group_{self.profile.user.username}",
                    session=session,
                )
                self.group_id = group.id

            if not self.resource_id:
                resource = WialonResource(
                    owner=super_user,
                    name=f"resource_{self.profile.user.username}",
                    session=session,
                )
                self.resource_id = resource.id
        return super().save(**kwargs)


class TrackerAuthorizenetProfile(models.Model):
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="authorizenet_profile",
        primary_key=True,
    )
    id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"{self.profile.user}'s Authorizenet Profile"


class TrackerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        return f"{self.user}'s Profile"
