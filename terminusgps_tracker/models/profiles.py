from typing import Any

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _
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
from terminusgps.wialon.session import WialonSession


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

    def clean(self, **kwargs) -> None:
        if self.id is not None:
            if self.payments.filter().exists() and self.payments.count() > 4:
                raise ValidationError(
                    _("You cannot assign more than four payment methods.")
                )
            if self.addresses.filter().exists() and self.addresses.count() > 4:
                raise ValidationError(
                    _("You cannot assign more than four shipping addresses.")
                )
        return super().clean(**kwargs)

    def delete(self, *args, **kwargs) -> tuple[int, dict[str, int]]:
        if self.authorizenet_id:
            self.authorizenet_delete_customer_profile(profile_id=self.authorizenet_id)
        return super().delete(*args, **kwargs)

    @staticmethod
    def authorizenet_create_customer_profile(customer_id: int, email: str) -> int:
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

    @staticmethod
    def authorizenet_get_customer_profile(
        profile_id: int | None = None, merchant_id: int | None = None
    ) -> dict[str, Any] | None:
        if not profile_id or not merchant_id:
            raise ValueError("No 'profile_id' or 'merchant_id' provided.")

        request = getCustomerProfileRequest(merchantAuthentication=get_merchant_auth())
        if profile_id:
            request.customerProfileId = str(profile_id)
        elif merchant_id:
            request.merchantCustomerId = str(merchant_id)

        controller = getCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return response

    @staticmethod
    def authorizenet_update_customer_profile(merchant_id: int, email: str) -> None:
        request = updateCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            profile=customerProfileType(
                merchantCustomerId=str(merchant_id), email=email
            ),
        )

        controller = updateCustomerProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    @staticmethod
    def authorizenet_delete_customer_profile(profile_id: int) -> None:
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
