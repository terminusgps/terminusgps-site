from django.db import models
from django.conf import settings

from authorizenet.apicontrollers import createCustomerPaymentProfileController
from authorizenet.apicontractsv1 import (
    deleteCustomerPaymentProfileRequest,
    deleteCustomerPaymentProfileResponse,
    createCustomerPaymentProfileRequest,
    createCustomerPaymentProfileResponse,
    creditCardType,
    customerAddressType,
    customerPaymentProfileType,
    merchantAuthenticationType,
    paymentType,
)
from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth

from terminusgps_tracker.forms.payments import (
    PaymentMethodCreationForm,
    PaymentMethodDeletionForm,
)


class TrackerPaymentMethod(models.Model):
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        username: str = self.profile.user.username
        return f"{username}'s Payment Method #{self.authorizenet_id}"

    def save(self, form: PaymentMethodCreationForm | None = None, **kwargs) -> None:
        if form and form.is_valid():
            paymentProfile: customerPaymentProfileType = self._generate_payment_profile(
                form
            )
            merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
            testMode: bool = settings.DEBUG

            request = self._generate_create_payment_profile_request(
                paymentProfile=paymentProfile,
                merchantAuthentication=merchantAuthentication,
                testMode=testMode,
            )
            controller = createCustomerPaymentProfileController(request)
            controller.execute()
            response: createCustomerPaymentProfileResponse = controller.getresponse()
            if response.messages.statusCode != "Ok":
                raise ValueError(response.messages.message["text"].text)
            self.authorizenet_id = int(response.customerPaymentProfileId)
        super().save(**kwargs)

    def delete(self, form: PaymentMethodDeletionForm | None = None, **kwargs):
        if form and self.authorizenet_id:
            merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
            customerProfileId: str = str(self.profile.customerProfileId)
            customerPaymentProfileId: str = str(self.authorizenet_id)

            request = deleteCustomerPaymentProfileRequest(
                merchantAuthentication=merchantAuthentication,
                customerProfileId=customerProfileId,
                customerPaymentProfileId=customerPaymentProfileId,
            )
            controller = deleteCustomerPaymentProfileController(request)
            controller.execute()
            response: deleteCustomerPaymentProfileResponse = controller.getresponse()
            if response.messages.statusCode != "Ok":
                raise ValueError(response.messages.message["text"].text)
            self.authorizenet_id = None
        return super().delete(**kwargs)

    def _generate_create_payment_profile_request(
        self,
        paymentProfile: customerPaymentProfileType,
        merchantAuthentication: merchantAuthenticationType,
        testMode: bool = False,
    ) -> createCustomerPaymentProfileRequest:
        return createCustomerPaymentProfileRequest(
            merchantAuthentication=merchantAuthentication,
            paymentProfile=paymentProfile,
            validationMode="testMode" if testMode else "liveMode",
        )

    def _generate_payment_profile(
        self, form: PaymentMethodCreationForm
    ) -> customerPaymentProfileType:
        return customerPaymentProfileType(
            customerProfileId=self.profile.customerProfileId,
            payment=paymentType(
                creditCard=creditCardType(
                    cardNumber=form.cleaned_data["credit_card_number"],
                    expirationDate=f"{form.cleaned_data["credit_card_expiry_month"]}-{form.cleaned_data["credit_card_expiry_year"]}",
                    cardCode=form.cleaned_data["credit_card_ccv"],
                )
            ),
            billTo=customerAddressType(
                firstName=self.profile.first_name,
                lastName=self.profile.last_name,
                email=self.profile.email or self.profile.username,
                address=form.cleaned_data["address_street"],
                city=form.cleaned_data["address_city"],
                state=form.cleaned_data["address_state"],
                zip=form.cleaned_data["address_zip"],
                country=form.cleaned_data["address_country"],
                phoneNumber=form.cleaned_data["address_phone"],
            ),
            defaultPaymentProfile=self.is_default,
        )
