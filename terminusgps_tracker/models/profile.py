from typing import Any
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from authorizenet.apicontractsv1 import (
    merchantAuthenticationType,
    customerProfileType,
    createCustomerProfileRequest,
    getCustomerProfileRequest,
)
from authorizenet.apicontrollers import (
    createCustomerProfileController,
    getCustomerProfileController,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth


class TrackerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        return f"{self.user}'s Profile"

    @classmethod
    def get_authorizenet_customer_profile(
        cls, profile_id: int, issuer_info: bool = False
    ) -> dict[str, Any] | None:
        request = getCustomerProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(profile_id),
            includeIssuerInfo=issuer_info,
        )
        controller = getCustomerProfileController(request)
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return response

    def create_authorizenet_customer_profile(self) -> int:
        request = createCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=self.customerProfile,
            validationMode="testMode" if settings.DEBUG else "liveMode",
        )
        controller = createCustomerProfileController(request)
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.customerProfileId)

    @property
    def customerProfileId(self) -> str:
        return str(self.authorizenet_id)

    @property
    def customerProfile(self) -> customerProfileType:
        return customerProfileType(
            merchantCustomerId=str(self.user.pk), email=str(self.user.email)
        )

    @property
    def merchantAuthentication(self) -> merchantAuthenticationType:
        return get_merchant_auth()
