from typing import Any
from django.db import models
from django.conf import settings
from django.forms import Form

from authorizenet.apicontrollers import (
    createCustomerPaymentProfileController,
    deleteCustomerPaymentProfileController,
    getCustomerPaymentProfileController,
    validateCustomerPaymentProfileController,
)
from authorizenet.apicontractsv1 import (
    createCustomerPaymentProfileRequest,
    creditCardType,
    customerAddressType,
    customerPaymentProfileType,
    deleteCustomerPaymentProfileRequest,
    getCustomerPaymentProfileRequest,
    paymentType,
    validateCustomerPaymentProfileRequest,
)

from terminusgps.authorizenet.auth import get_merchant_auth, get_environment


class TrackerPaymentMethod(models.Model):
    is_default = models.BooleanField(default=False)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="payments",
    )

    class Meta:
        verbose_name = "payment method"
        verbose_name_plural = "payment methods"

    def __str__(self) -> str:
        return f"Payment Method #{self.authorizenet_id}"

    def save(self, form: Form | None = None, **kwargs) -> None:
        if form and form.is_valid():
            self.is_default = form.cleaned_data.get("is_default", False)
            self.authorizenet_id = self.authorizenet_create_payment_profile(
                form, form.cleaned_data.get("is_default", False)
            )
        return super().save(**kwargs)

    def delete(self, **kwargs):
        if self.authorizenet_id and self.profile.authorizenet_id:
            profile_id = int(self.profile.authorizenet_id)
            payment_id = int(self.authorizenet_id)
            self.authorizenet_delete_payment_profile(profile_id, payment_id)
        return super().delete(**kwargs)

    def set_as_default(self) -> None:
        raise NotImplementedError("TODO")

    def authorizenet_create_payment_profile(
        self, form: Form, default: bool = False
    ) -> int:
        request = createCustomerPaymentProfileRequest(
            customerProfileId=str(self.profile.authorizenet_id),
            merchantAuthentication=get_merchant_auth(),
            paymentProfile=self.generate_payment_profile(form, default),
            validationMode="testMode" if settings.DEBUG else "liveMode",
        )

        controller = createCustomerPaymentProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.customerPaymentProfileId)

    @classmethod
    def authorizenet_validate_payment_profile(
        cls, profile_id: int, payment_id: int
    ) -> None:
        request = validateCustomerPaymentProfileRequest(
            customerPaymentProfileId=str(payment_id),
            customerProfileId=str(profile_id),
            merchantAuthentication=get_merchant_auth(),
            validationMode="testMode" if settings.DEBUG else "liveMode",
        )

        controller = validateCustomerPaymentProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    @classmethod
    def authorizenet_delete_payment_profile(
        cls, profile_id: int, payment_id: int
    ) -> None:
        request = deleteCustomerPaymentProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(profile_id),
            customerPaymentProfileId=str(payment_id),
        )

        controller = deleteCustomerPaymentProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    @classmethod
    def authorizenet_get_payment_profile(
        cls, profile_id: int, payment_id: int, unmaskExpirationDate: bool = False
    ) -> dict[str, Any]:
        request = getCustomerPaymentProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=str(profile_id),
            customerPaymentProfileId=str(payment_id),
            unmaskExpirationDate=unmaskExpirationDate,
        )

        controller = getCustomerPaymentProfileController(request)
        controller.setenvironment(get_environment())
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

        return {
            "customerProfileId": response.paymentProfile.customerProfileId,
            "customerPaymentProfileId": response.paymentProfile.customerPaymentProfileId,
            "billTo": {
                "firstName": response.paymentProfile.billTo.firstName,
                "lastName": response.paymentProfile.billTo.lastName,
                "address": response.paymentProfile.billTo.address,
                "city": response.paymentProfile.billTo.city,
                "state": response.paymentProfile.billTo.state,
                "zip": response.paymentProfile.billTo.zip,
                "phoneNumber": response.paymentProfile.billTo.phoneNumber,
            },
            "payment": {
                "creditCard": {
                    "cardNumber": response.paymentProfile.payment.creditCard.cardNumber,
                    "expirationDate": response.paymentProfile.payment.creditCard.expirationDate,
                    "cardType": response.paymentProfile.payment.creditCard.cardType,
                }
            },
        }

    def generate_payment_profile(
        self, form: Form, default: bool = False
    ) -> customerPaymentProfileType:
        return customerPaymentProfileType(
            defaultPaymentProfile=default,
            billTo=self.generate_billing_address(form),
            payment=self.generate_payment(form),
        )

    @classmethod
    def generate_billing_address(cls, form: Form) -> customerAddressType:
        address = customerAddressType(
            firstName=form.cleaned_data["address_first_name"],
            lastName=form.cleaned_data["address_last_name"],
            address=form.cleaned_data["address_street"],
            city=form.cleaned_data["address_city"],
            state=form.cleaned_data["address_state"],
            zip=form.cleaned_data["address_zip"],
            country=form.cleaned_data["address_country"],
            phoneNumber=form.cleaned_data["address_phone"],
        )
        if form.cleaned_data.get("address_phone"):
            address.phoneNumber = form.cleaned_data["address_phone"]
        return address

    @classmethod
    def generate_payment(cls, form: Form) -> paymentType:
        month: str = form.cleaned_data["credit_card_expiry_month"]
        year: str = form.cleaned_data["credit_card_expiry_year"]
        cardNumber: str = form.cleaned_data["credit_card_number"]
        cardCode: str = form.cleaned_data["credit_card_ccv"]
        expirationDate: str = f"{month}-{year}"

        return paymentType(
            creditCard=creditCardType(
                cardNumber=cardNumber, cardCode=cardCode, expirationDate=expirationDate
            )
        )
