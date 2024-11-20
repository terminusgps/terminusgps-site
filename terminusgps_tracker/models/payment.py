from django.db import models
from django.conf import settings

from authorizenet.apicontrollers import (
    createCustomerPaymentProfileController,
    createCustomerShippingAddressController,
    deleteCustomerPaymentProfileController,
    deleteCustomerShippingAddressController,
    getCustomerShippingAddressController,
    getCustomerPaymentProfileController,
)
from authorizenet.apicontractsv1 import (
    createCustomerPaymentProfileRequest,
    createCustomerPaymentProfileResponse,
    createCustomerShippingAddressRequest,
    createCustomerShippingAddressResponse,
    getCustomerShippingAddressRequest,
    getCustomerShippingAddressResponse,
    getCustomerPaymentProfileRequest,
    getCustomerPaymentProfileResponse,
    deleteCustomerPaymentProfileRequest,
    deleteCustomerPaymentProfileResponse,
    deleteCustomerShippingAddressRequest,
    deleteCustomerShippingAddressResponse,
    creditCardType,
    customerAddressType,
    customerPaymentProfileType,
    merchantAuthenticationType,
    paymentType,
)
from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth

from terminusgps_tracker.forms.payments import (
    PaymentMethodCreationForm,
    ShippingAddressCreationForm,
)


class TrackerShippingAddress(models.Model):
    is_default = models.BooleanField(default=False)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    profile = models.OneToOneField(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    class Meta:
        verbose_name = "profile address"
        verbose_name_plural = "profile addresses"

    def __str__(self) -> str:
        return f"{self.profile.user.username}'s Shipping Address"

    def save(self, form: ShippingAddressCreationForm | None = None, **kwargs) -> None:
        if form and form.is_valid():
            self.authorizenet_id = self.create_authorizenet_address(form)
        return super().save(**kwargs)

    def delete(self, **kwargs):
        if self.authorizenet_id is not None:
            self.delete_authorizenet_address(self.authorizenet_id)
        return super().delete(**kwargs)

    def create_authorizenet_address(
        self, form: ShippingAddressCreationForm
    ) -> int | None:
        request = self._gen_create_request(form=form)
        controller = createCustomerShippingAddressController(request)
        controller.execute()
        response: createCustomerShippingAddressResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

        return int(response.customerAddressId)

    def delete_authorizenet_address(self, address_id: int) -> None:
        request = self._gen_delete_request(address_id)
        controller = deleteCustomerShippingAddressController(request)
        controller.execute()
        response: deleteCustomerShippingAddressResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    def get_authorizenet_address(self, address_id: int) -> customerAddressType:
        request = self._gen_get_request(address_id)
        controller = getCustomerShippingAddressController(request)
        controller.execute()
        response: getCustomerShippingAddressResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return response.address

    def _gen_get_request(self, address_id: int) -> getCustomerShippingAddressRequest:
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        return getCustomerShippingAddressRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=self.profile.customerProfileId,
            customerAddressId=str(address_id),
        )

    def _gen_create_request(
        self, form: ShippingAddressCreationForm
    ) -> createCustomerShippingAddressRequest:
        if form.cleaned_data.get("is_default", False):
            self.is_default = True

        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        return createCustomerShippingAddressRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=self.profile.customerProfileId,
            defaultShippingAddress=form.cleaned_data["is_default"],
            address=customerAddressType(
                firstName=self.profile.firstName,
                lastName=self.profile.lastName,
                address=form.cleaned_data["address_street"],
                city=form.cleaned_data["address_city"],
                state=form.cleaned_data["address_state"],
                zip=form.cleaned_data["address_zip"],
                country=form.cleaned_data["address_country"],
                phoneNumber=form.cleaned_data["address_phone"],
            ),
        )

    def _gen_delete_request(
        self, authorizenet_id: int
    ) -> deleteCustomerShippingAddressRequest:
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        return deleteCustomerShippingAddressRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=self.profile.customerProfileId,
            customerAddressId=str(authorizenet_id),
        )


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

    def __str__(self) -> str:
        username: str = self.profile.user.username
        return f"{username}'s Payment Method #{self.authorizenet_id}"

    def save(self, form: PaymentMethodCreationForm | None = None, **kwargs) -> None:
        if form and form.is_valid():
            self.authorizenet_id = self.create_authorizenet_payment_profile(form)
        return super().save(**kwargs)

    def delete(self, **kwargs):
        if self.authorizenet_id is not None:
            self.delete_authorizenet_payment_profile(self.authorizenet_id)
        return super().delete(**kwargs)

    def delete_authorizenet_payment_profile(self, payment_profile_id: int) -> None:
        request = self._gen_delete_request(payment_profile_id)
        controller = deleteCustomerPaymentProfileController(request)
        controller.execute()
        response: deleteCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)

    def create_authorizenet_payment_profile(
        self, form: PaymentMethodCreationForm
    ) -> int | None:
        request = self._gen_create_request(form=form)
        controller = createCustomerPaymentProfileController(request)
        controller.execute()
        response: createCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return int(response.customerPaymentProfileId)

    def get_authorizenet_payment_profile(
        self, payment_profile_id: int
    ) -> customerPaymentProfileType:
        request = self._gen_get_request(payment_profile_id)
        controller = getCustomerPaymentProfileController(request)
        controller.execute()
        response: getCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(response.messages.message[0]["text"].text)
        return response.paymentProfile

    def _gen_get_request(
        self, payment_profile_id: int
    ) -> getCustomerPaymentProfileRequest:
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        return getCustomerPaymentProfileRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=self.profile.customerProfileId,
            customerPaymentProfileId=str(payment_profile_id),
        )

    def _gen_delete_request(
        self, payment_profile_id: int
    ) -> deleteCustomerPaymentProfileRequest:
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        return deleteCustomerPaymentProfileRequest(
            merchantAuthentication=merchantAuthentication,
            customerProfileId=self.profile.customerProfileId,
            customerPaymentProfileId=str(payment_profile_id),
        )

    def _gen_create_request(
        self, form: PaymentMethodCreationForm, testMode: bool | None = None
    ) -> createCustomerPaymentProfileRequest:
        if testMode is None:
            testMode = settings.DEBUG

        month, year = (
            form.cleaned_data["credit_card_expiry_month"],
            form.cleaned_data["credit_card_expiry_year"],
        )
        merchantAuthentication: merchantAuthenticationType = get_merchant_auth()
        expirationDate: str = "-".join({month, year})
        return createCustomerPaymentProfileRequest(
            validationMode="testMode" if testMode else "liveMode",
            merchantAuthentication=merchantAuthentication,
            customerProfileId=self.profile.customerProfileId,
            paymentProfile=customerPaymentProfileType(
                defaultPaymentProfile=form.cleaned_data["is_default"],
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
                        expirationDate=expirationDate,
                        cardCode=form.cleaned_data["credit_card_ccv"],
                    )
                ),
            ),
        )
