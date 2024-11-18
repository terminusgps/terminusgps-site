from authorizenet.apicontractsv1 import (
    creditCardType,
    customerAddressType,
    customerPaymentProfileType,
    paymentType,
    createCustomerPaymentProfileRequest,
    createCustomerPaymentProfileResponse,
    deleteCustomerPaymentProfileRequest,
    deleteCustomerPaymentProfileResponse,
)
from authorizenet.apicontrollers import createCustomerPaymentProfileController
from django.db import models

from terminusgps_tracker.forms.payments import (
    PaymentMethodCreationForm,
    PaymentMethodDeletionForm,
)
from terminusgps_tracker.integrations.authorizenet.auth import get_merchant_auth


class TrackerPaymentMethod(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    is_default = models.BooleanField(default=False)
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"Paymet Method #{self.id}"

    def save(self, **kwargs) -> None:
        if self.id is None:
            self.id = self.create_authorizenet_payment_profile(form=kwargs.get("form"))
        super().save(**kwargs)

    def delete(self, *args, **kwargs):
        self.delete_authorizenet_payment_profile(kwargs.get("form"))
        return super().delete(*args, **kwargs)

    def create_authorizenet_payment_profile(
        self, form: PaymentMethodCreationForm | None = None
    ) -> str:
        if form is None:
            raise ValueError("Cannot create payment profile without form")
        if self.profile is None:
            raise ValueError("Cannot create payment profile without customer profile")

        request = self._generate_create_request(form)
        controller = createCustomerPaymentProfileController(request)
        controller.execute()
        response: createCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to create customer profile: {response.message.messages["text"].text}"
            )
        return str(response.customerPaymentProfileId)

    def delete_authorizenet_payment_profile(
        self, form: PaymentMethodDeletionForm | None = None
    ) -> None:
        if form is None:
            raise ValueError("Cannot delete payment profile without form")
        if self.profile is None:
            raise ValueError("Cannot delete payment profile without customer profile")

        request = self._generate_delete_request(form)
        controller = deleteCustomerPaymentProfileRequest(request)
        controller.execute()
        response: deleteCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to delete customer profile: {response.message.messages["text"].text}"
            )
        return

    def _generate_delete_request(self, form: PaymentMethodDeletionForm):
        profile_id = self.profile.authorizenet_profile_id
        payment_profile_id = self.id

        return deleteCustomerPaymentProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=profile_id,
            customerPaymentProfileId=payment_profile_id,
        )

    def _generate_create_request(self, form: PaymentMethodCreationForm):
        expiry_date = f"{form.cleaned_data["credit_card_expiry_month"]}-{form.cleaned_data["credit_card_expiry_year"]}"
        first_name, last_name = (
            self.profile.user.first_name,
            self.profile.user.last_name,
        )
        customer_profile_id = str(self.profile.authorizenet_profile_id)

        return createCustomerPaymentProfileRequest(
            merchantAuthentication=get_merchant_auth(),
            customerProfileId=customer_profile_id,
            paymentProfile=customerPaymentProfileType(
                billTo=customerAddressType(
                    firstName=first_name,
                    lastName=last_name,
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
                        expirationDate=expiry_date,
                        cardCode=form.cleaned_data["credit_card_ccv"],
                    )
                ),
                defaultPaymentProfile=bool(form.cleaned_data["is_default"] == "on"),
            ),
        )
