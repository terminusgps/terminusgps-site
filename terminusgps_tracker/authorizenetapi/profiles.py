from decimal import Decimal

from django.contrib.auth.models import User
from authorizenet.apicontractsv1 import (
    ARBCreateSubscriptionRequest,
    ARBSubscriptionUnitEnum,
    creditCardType,
    customerAddressType,
    customerPaymentProfileType,
    customerProfileType,
    createCustomerProfileRequest,
    createCustomerPaymentProfileRequest,
    createCustomerProfileResponse,
    createCustomerPaymentProfileResponse,
    merchantAuthenticationType,
    createCustomerShippingAddressRequest,
    createCustomerShippingAddressResponse,
    getCustomerShippingAddressRequest,
    getCustomerShippingAddressResponse,
    paymentScheduleType,
    paymentType,
    subscriptionCustomerProfileType,
)
from authorizenet.apicontrollers import (
    createCustomerPaymentProfileController,
    createCustomerProfileController,
    createCustomerShippingAddressController,
    getCustomerShippingAddressController,
)

from terminusgps_tracker.authorizenetapi.auth import get_merchant_auth
from terminusgps_tracker.models import CustomerProfile


class AuthorizenetProfile:
    def __init__(self, user: User) -> None:
        self.profile, _ = CustomerProfile.objects.get_or_create(user=user)
        self.merchantCustomerId = str(self.profile.user.pk)
        if self.profile.authorizenet_profile_id:
            self._id = str(self.profile.authorizenet_profile_id)
        else:
            self._id = self.create()
            self.profile.authorizenet_profile_id = self._id
            self.profile.save()

    @property
    def merchantAuthentication(self) -> merchantAuthenticationType:
        return get_merchant_auth()

    @property
    def id(self) -> int | None:
        return int(self._id) if self._id else None

    def create_subscription(self, tier: int = 1, total_months: int = 12) -> None:
        request = ARBCreateSubscriptionRequest(
            merchantAuthentication=self.merchantAuthentication,
            subscription=subscriptionCustomerProfileType(
                name="Terminus Subscription",
                paymentSchedule=paymentScheduleType(
                    interval={
                        "length": str(total_months),
                        "unit": ARBSubscriptionUnitEnum.months,
                    }
                ),
                amount=str(Decimal(11.99)),
                trialAmount=str(Decimal(0.00)),
                profile=customerPaymentProfileType(
                    customerProfileId=str(self.profile.authorizenet_profile_id),
                    customerPaymentProfileId=str(self.profile.authorizenet_payment_id),
                    customerAddressId=str(self.profile.authorizenet_address_id),
                ),
            ),
        )

    def create(self) -> str:
        request = createCustomerProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            profile=customerProfileType(merchantCustomerId=self.merchantCustomerId),
        )
        controller = createCustomerProfileController(request)
        controller.execute()
        response: createCustomerProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to create customer profile: {response.messages.message[0]["text"].text}"
            )
        return str(response.customerProfileId)

    def create_payment_profile(
        self, credit_card: creditCardType, default: bool = True
    ) -> None:
        request = createCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=str(self.id),
            payment=paymentType(creditCard=credit_card),
            defaultPaymentProfile=default,
        )
        controller = createCustomerPaymentProfileController(request)
        controller.execute()
        response: createCustomerPaymentProfileResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly create payment profile: {response.messages.message[0]["text"].text}"
            )
        self.profile.authorizenet_payment_id = response.customerPaymentProfileId
        self.profile.save()

    def save_address(self, address: customerAddressType, default: bool = True) -> None:
        request = createCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=str(self.id),
            address=address,
            defaultShippingAddress=default,
        )
        controller = createCustomerShippingAddressController(request)
        controller.execute()
        response: createCustomerShippingAddressResponse = controller.getresponse()
        if not response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly create customer address: {response.messages.message[0]["text"].text}"
            )
        self.profile.authorizenet_address_id = str(response.customerAddressId)
        self.profile.save()

    def get_address(self) -> customerAddressType:
        if self.profile.authorizenet_address_id is not None:
            request = getCustomerShippingAddressRequest(
                merchantAuthentication=self.merchantAuthentication,
                customerProfileId=str(self.profile.authorizenet_profile_id),
                customerAddressId=str(self.profile.authorizenet_address_id),
            )
        else:
            request = getCustomerShippingAddressRequest(
                merchantAuthentication=self.merchantAuthentication,
                customerProfileId=str(self.profile.authorizenet_profile_id),
            )
        controller = getCustomerShippingAddressController(request)
        response: getCustomerShippingAddressResponse = controller.getresponse()
        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly retrieve customer address: {response.messages.message[0]["text"].text}"
            )
        return customerAddressType(**response.address)
