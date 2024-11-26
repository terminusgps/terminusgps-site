from typing import Any
from django.db import models

from authorizenet.apicontractsv1 import (
    createCustomerShippingAddressRequest,
    customerAddressType,
    getCustomerShippingAddressRequest,
    merchantAuthenticationType,
)
from authorizenet.apicontrollers import (
    createCustomerShippingAddressController,
    getCustomerShippingAddressController,
)

from terminusgps_tracker.forms import ShippingAddressCreationForm
from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth


class TrackerShippingAddress(models.Model):
    is_default = models.BooleanField(default=False)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    class Meta:
        verbose_name = "shipping address"
        verbose_name_plural = "shipping addresses"

    def __str__(self) -> str:
        return f"{self.profile.user.username}'s Shipping Address"

    def save(self, form: ShippingAddressCreationForm | None = None, **kwargs) -> None:
        if form and form.is_valid():
            self.is_default = form.cleaned_data["is_default"]
            self.authorizenet_id = self.create_authorizenet_address(form)
        return super().save(**kwargs)

    def create_authorizenet_address(self, form: ShippingAddressCreationForm) -> int:
        request = createCustomerShippingAddressRequest(
            merchantAuthentication=self.profile.merchantAuthentication,
            customerProfileId=self.profile.customerProfileId,
            defaultShippingAddress=form.cleaned_data["is_default"],
            address=customerAddressType(
                firstName=self.profile.user.first_name,
                lastName=self.profile.user.last_name,
                address=form.cleaned_data["address_street"],
                city=form.cleaned_data["address_city"],
                state=form.cleaned_data["address_state"],
                zip=form.cleaned_data["address_zip"],
                country=form.cleaned_data["address_country"],
                phoneNumber=form.cleaned_data["address_phone"],
            ),
        )

        controller = createCustomerShippingAddressController(request)
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.customerAddressId)

    @classmethod
    def get_authorizenet_address(
        cls, profile_id: int, address_id: int | None = None
    ) -> dict[str, Any]:
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        request = getCustomerShippingAddressRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=str(profile_id),
        )
        if address_id is not None:
            request.customerAddressId = str(address_id)

        controller = getCustomerShippingAddressController(request)
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return {
            "customerAddressId": response.address.customerAddressId,
            "address": {
                "street": response.address.address,
                "city": response.address.city,
                "state": response.address.state,
                "zip": response.address.zip,
                "country": response.address.country,
                "phone": response.address.phoneNumber,
            },
        }
