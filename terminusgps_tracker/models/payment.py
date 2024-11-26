from typing import Any
from django.db import models
from django.conf import settings

from authorizenet.apicontrollers import (
    createCustomerPaymentProfileController,
    deleteCustomerPaymentProfileController,
    getCustomerPaymentProfileController,
)
from authorizenet.apicontractsv1 import (
    createCustomerPaymentProfileRequest,
    createCustomerPaymentProfileResponse,
    getCustomerPaymentProfileRequest,
    deleteCustomerPaymentProfileRequest,
    creditCardType,
    customerAddressType,
    customerPaymentProfileType,
    merchantAuthenticationType,
    paymentType,
)

from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth
from terminusgps_tracker.forms.payments import PaymentMethodCreationForm


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

    def save(self, form: PaymentMethodCreationForm | None = None, **kwargs) -> None:
        if form and form.is_valid():
            self.is_default = form.cleaned_data["is_default"]
            self.authorizenet_id = self.create_authorizenet_payment_profile(form)
        return super().save(**kwargs)

    def delete(self, **kwargs):
        if self.authorizenet_id:
            profile_id = int(self.profile.customerProfileId)
            payment_id = int(self.authorizenet_id)
            self.delete_authorizenet_payment_profile(profile_id, payment_id)
        return super().delete(**kwargs)

    def create_authorizenet_payment_profile(
        self, form: PaymentMethodCreationForm
    ) -> int:
        request = createCustomerPaymentProfileRequest(
            merchantAuthentication=self.profile.merchantAuthentication,
            validationMode="testMode" if settings.DEBUG else "liveMode",
            customerProfileId=self.profile.customerProfileId,
            paymentProfile=customerPaymentProfileType(
                defaultPaymentProfile=self.is_default,
                billTo=customerAddressType(
                    firstName=self.profile.firstName,
                    lastName=self.profile.lastName,
                    address=form.cleaned_data["address_street"],
                    city=form.cleaned_data["address_city"],
                    state=form.cleaned_data["address_state"],
                    zip=form.cleaned_data["address_zip"],
                    country=form.cleaned_data["address_country"],
                    phoneNumber=form.cleaned_data["address_phone"],
                ),
                payment=paymentType(
                    creditCard=creditCardType(
                        cardNumber=form.cleaned_data["credit_card_number"],
                        cardCode=form.cleaned_data["credit_card_ccv"],
                        expirationDate=f"{form.cleaned_data["credit_card_expiry_month"]}-{form.cleaned_data["credit_card_expiry_year"]}",
                    )
                ),
            ),
        )

        controller = createCustomerPaymentProfileController(request)
        controller.execute()
        response: createCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.customerPaymentProfileId)

    @classmethod
    def delete_authorizenet_payment_profile(
        cls, profile_id: int, payment_id: int | None = None
    ) -> None:
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        request = deleteCustomerPaymentProfileRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=str(profile_id),
        )

        if payment_id is not None:
            request.customerPaymentProfileId = str(payment_id)
        controller = deleteCustomerPaymentProfileController(request)
        controller.execute()
        response = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return

    @classmethod
    def get_authorizenet_payment_profile(
        cls, profile_id: int, payment_id: int | None = None
    ) -> dict[str, Any]:
        defaultPaymentMethod: bool = False
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        request = getCustomerPaymentProfileRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=str(profile_id),
        )

        if payment_id is not None:
            request.customerPaymentProfileId = str(payment_id)
            defaultPaymentMethod: bool = TrackerPaymentMethod.objects.get(
                authorizenet_id=payment_id
            ).is_default
        controller = getCustomerPaymentProfileController(request)
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
                "creditCardNumber": response.paymentProfile.payment.creditCard.cardNumber,
                "creditCardExpirationDate": response.paymentProfile.payment.creditCard.expirationDate,
                "creditCardType": response.paymentProfile.payment.creditCard.cardType,
                "defaultPaymentMethod": defaultPaymentMethod,
            },
        }
