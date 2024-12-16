from typing import Any
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

from terminusgps.authorizenet.auth import get_merchant_auth, get_environment


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
        return super().save(**kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        if self.authorizenet_id:
            self.authorizenet_delete_customer_profile(profile_id=self.authorizenet_id)
        return super().delete(*args, **kwargs)

    @classmethod
    def authorizenet_create_customer_profile(cls, customer_id: int, email: str) -> int:
        request = createCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            profile=customerProfileType(
                merchantCustomerId=str(customer_id), email=email
            ),
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
