from typing import Any
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from authorizenet.apicontractsv1 import (
    customerProfileType,
    createCustomerProfileRequest,
    getCustomerProfileRequest,
    deleteCustomerProfileRequest,
    updateCustomerProfileRequest,
)
from authorizenet.apicontrollers import (
    createCustomerProfileController,
    deleteCustomerProfileController,
    getCustomerProfileController,
    updateCustomerProfileController,
)

from terminusgps_tracker.integrations.authorizenet import (
    get_merchant_auth,
    get_environment,
)
from terminusgps_tracker.integrations.wialon.items import (
    WialonUnitGroup,
    WialonUser,
    WialonResource,
)
from terminusgps_tracker.integrations.wialon.session import WialonSession
from terminusgps_tracker.integrations.wialon.utils import gen_wialon_password


class TrackerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_group_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_resource_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_end_user_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_super_user_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        return f"{self.user}'s Profile"

    def save(self, **kwargs) -> None:
        if self.authorizenet_id is None:
            self.authorizenet_id = self.authorizenet_create_customer_profile(
                customer_id=self.user.pk, email=self.user.username
            )

        with WialonSession() as session:
            admin: WialonUser = self._get_admin_user(session)
            if self.wialon_super_user_id is None:
                super_user = self.wialon_create_user(
                    owner=admin,
                    name=f"super_{self.user.username}",
                    password=gen_wialon_password(),
                    session=session,
                )
                self.wialon_super_user_id = super_user.id

            if self.wialon_end_user_id is None:
                super_user = WialonUser(
                    id=str(self.wialon_super_user_id), session=session
                )
                end_user = self.wialon_create_user(
                    owner=super_user,
                    name=f"super_{self.user.username}",
                    password=gen_wialon_password(),
                    session=session,
                )
                self.wialon_end_user_id = end_user.id

            if self.wialon_group_id is None:
                super_user = WialonUser(
                    id=str(self.wialon_super_user_id), session=session
                )
                group = self.wialon_create_group(
                    owner=super_user,
                    name=f"group_{self.user.username}",
                    session=session,
                )
                self.wialon_group_id = group.id

            if self.wialon_resource_id is None:
                super_user = WialonUser(
                    id=str(self.wialon_super_user_id), session=session
                )
                resource = self.wialon_create_resource(
                    owner=super_user,
                    name=f"resource_{self.user.username}",
                    session=session,
                )
                self.wialon_resource_id = resource.id

        return super().save(**kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        if self.authorizenet_id:
            self.authorizenet_delete_customer_profile(profile_id=self.authorizenet_id)
        return super().delete(*args, **kwargs)

    def _get_admin_user(
        self, session: WialonSession, alt_id: int | None = None
    ) -> WialonUser:
        admin_id: int = alt_id if alt_id else settings.WIALON_ADMIN_ID
        return WialonUser(id=str(admin_id), session=session)

    @classmethod
    def wialon_create_resource(
        cls, owner: WialonUser, name: str, session: WialonSession
    ) -> WialonResource:
        return WialonResource(owner_id=owner.id, name=name, session=session)

    @classmethod
    def wialon_create_group(
        cls, owner: WialonUser, name: str, session: WialonSession
    ) -> WialonUnitGroup:
        return WialonUnitGroup(owner_id=owner.id, name=name, session=session)

    @classmethod
    def wialon_delete_group(cls, group_id: int, session: WialonSession) -> None:
        group = WialonUnitGroup(id=str(group_id), session=session)
        group.delete()

    @classmethod
    def wialon_delete_resource(cls, resource_id: int, session: WialonSession) -> None:
        resource = WialonResource(id=str(resource_id), session=session)
        resource.delete()

    @classmethod
    def wialon_create_user(
        cls, owner: WialonUser, name: str, password: str, session: WialonSession
    ) -> WialonUser:
        return WialonUser(
            owner_id=owner.id, name=name, password=password, session=session
        )

    @classmethod
    def wialon_delete_user(cls, user_id: int, session: WialonSession) -> None:
        user = WialonUser(id=str(user_id), session=session)
        user.delete()

    @classmethod
    def authorizenet_create_customer_profile(cls, customer_id: int, email: str) -> int:
        request = createCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            profile=customerProfileType(merchantCustomerId=customer_id, email=email),
        )

        controller = createCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.customerProfileId)

    @classmethod
    def authorizenet_get_customer_profile(
        cls, profile_id: int | None = None, merchant_id: int | None = None
    ) -> dict[str, Any] | None:
        if not profile_id or not merchant_id:
            raise ValueError("No 'profile_id' or 'merchant_id' provided.")

        request = getCustomerProfileRequest(merchantAuthentication=get_merchant_auth())
        if profile_id:
            request.customerProfileId = str(profile_id)
        if merchant_id:
            request.merchantCustomerId = str(merchant_id)

        controller = getCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

        return response

    @classmethod
    def authorizenet_update_customer_profile(cls, merchant_id: int) -> None:
        request = updateCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            merchantCustomerId=str(merchant_id),
        )

        controller = updateCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    @classmethod
    def authorizenet_delete_customer_profile(cls, profile_id: int) -> None:
        request = deleteCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(profile_id),
        )

        controller = deleteCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
