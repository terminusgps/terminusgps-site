from typing import Any
from django.forms import Form
from django.db import models

from authorizenet.apicontractsv1 import (
    createCustomerShippingAddressRequest,
    customerAddressType,
    deleteCustomerShippingAddressRequest,
    getCustomerShippingAddressRequest,
)
from authorizenet.apicontrollers import (
    createCustomerShippingAddressController,
    deleteCustomerShippingAddressController,
    getCustomerShippingAddressController,
)

from terminusgps.authorizenet.auth import get_merchant_auth, get_environment


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
        return f"Address #{self.authorizenet_id}"

    def save(self, form: Form | None = None, **kwargs) -> None:
        if form and form.is_valid():
            self.is_default = form.cleaned_data["is_default"]
            self.authorizenet_id = self.authorizenet_create_shipping_address(form)
        return super().save(**kwargs)

    def delete(self, **kwargs):
        if self.authorizenet_id:
            profile_id = int(self.profile.authorizenet_id)
            address_id = int(self.authorizenet_id)
            self.authorizenet_delete_shipping_address(profile_id, address_id)
        return super().delete(**kwargs)

    def authorizenet_create_shipping_address(self, form: Form) -> int:
        request = createCustomerShippingAddressRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(self.profile.authorizenet_id),
            address=self.generate_shipping_address(form),
            defaultShippingAddress=form.cleaned_data["is_default"],
        )

        controller = createCustomerShippingAddressController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.customerAddressId)

    @classmethod
    def authorizenet_get_shipping_address(
        cls, profile_id: int, address_id: int
    ) -> dict[str, Any]:
        request = getCustomerShippingAddressRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(profile_id),
            customerAddressId=str(address_id),
        )

        controller = getCustomerShippingAddressController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return {
            "customerAddressId": response.address.customerAddressId,
            "address": {
                "firstName": response.address.firstName,
                "lastName": response.address.lastName,
                "street": response.address.address,
                "city": response.address.city,
                "state": response.address.state,
                "zip": response.address.zip,
                "country": response.address.country,
                "phone": response.address.phoneNumber,
            },
        }

    @classmethod
    def authorizenet_delete_shipping_address(
        cls, profile_id: int, address_id: int
    ) -> None:
        request = deleteCustomerShippingAddressRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(profile_id),
            customerAddressId=str(address_id),
        )

        controller = deleteCustomerShippingAddressController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    @classmethod
    def generate_shipping_address(cls, form: Form) -> customerAddressType:
        return customerAddressType(
            firstName=form.cleaned_data["address_first_name"],
            lastName=form.cleaned_data["address_last_name"],
            address=form.cleaned_data["address_street"],
            city=form.cleaned_data["address_city"],
            state=form.cleaned_data["address_state"],
            zip=form.cleaned_data["address_zip"],
            country=form.cleaned_data["address_country"],
            phoneNumber=form.cleaned_data["address_phone"],
        )
