from datetime import datetime
from typing import Optional
from django.contrib.auth.models import User

from authorizenet.apicontractsv1 import (
    ARBCreateSubscriptionRequest,
    ARBCreateSubscriptionResponse,
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
    paymentScheduleTypeInterval,
    paymentType,
    subscriptionCustomerProfileType,
)
from authorizenet.apicontrollers import (
    ARBCreateSubscriptionController,
    createCustomerPaymentProfileController,
    createCustomerProfileController,
    createCustomerShippingAddressController,
    getCustomerShippingAddressController,
)
from djmoney.money import Money

from terminusgps_tracker.authorizenetapi.auth import get_merchant_auth
from terminusgps_tracker.models import CustomerProfile


# Make a profile, add an address, add a payment profile, create a subscription
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

    def _generate_subscription(
        self,
        schedule: paymentScheduleType,
        amount: Money,
        name: str = "Terminus GPS Subscription",
    ) -> subscriptionCustomerProfileType:
        return subscriptionCustomerProfileType(
            name=name,
            paymentSchedule=schedule,
            amount=amount,
            profile=customerProfileType(
                customerProfileId=str(self.profile.authorizenet_profile_id),
                customerAddressId=str(self.profile.authorizenet_address_id),
            ),
        )

    def _generate_schedule(
        self, start_date: Optional[datetime] = None, total_months: int = 12
    ) -> paymentScheduleType:
        return paymentScheduleType(
            interval=paymentScheduleTypeInterval(
                length=1, unit=ARBSubscriptionUnitEnum.months
            ),
            startDate=start_date if start_date else datetime.now(),
            totalOccurances=total_months,
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

    def create_shipping_address(
        self, address: customerAddressType, default: bool = True
    ) -> None:
        request = createCustomerShippingAddressRequest(
            merchantAuthentication=self.merchantAuthentication,
            address=address,
            customerProfileId=str(self.profile.authorizenet_profile_id),
            defaultShippingAddress=default,
        )
        controller = createCustomerShippingAddressController(request)
        controller.execute()
        response: createCustomerShippingAddressResponse = controller.getresponse()

        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly save customer address: {response.messages.message[0]["text"].text}"
            )
        self.profile.authorizenet_address_id = str(response.customerAddressId)
        self.profile.save()

    def create_payment_profile(
        self,
        billing_address: customerAddressType,
        card_number: str,
        card_expiry: str,
        default: bool = True,
    ) -> None:
        request = createCustomerPaymentProfileRequest(
            merchantAuthentication=self.merchantAuthentication,
            customerProfileId=str(self.profile.authorizenet_profile_id),
            paymentProfile=customerPaymentProfileType(
                billTo=billing_address,
                payment=paymentType(
                    creditCard=creditCardType(
                        cardNumber=card_number, expirationDate=card_expiry
                    )
                ),
            ),
        )
        controller = createCustomerPaymentProfileController(request)
        controller.execute()
        response: createCustomerPaymentProfileResponse = controller.getresponse()

        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly create payment profile: {response.messages.message[0]["text"].text}"
            )
        self.profile.authorizenet_payment_id = str(response.customerPaymentProfileId)
        self.profile.save()

    def create_subscription(
        self,
        name: str = "Terminus GPS Subscription",
        total_months: int = 12,
        rate: float = 18.99,
    ) -> None:
        if not self.profile.authorizenet_profile_id:
            raise ValueError(
                f"Invalid profile id, got: {self.profile.authorizenet_profile_id}"
            )
        if not self.profile.authorizenet_address_id:
            raise ValueError(
                f"Invalid address id, got: {self.profile.authorizenet_address_id}"
            )

        monthly_rate: Money = Money(rate, "USD")
        total_amount: Money = monthly_rate * total_months
        schedule = self._generate_schedule(total_months=total_months)
        request = ARBCreateSubscriptionRequest(
            merchantAuthentication=self.merchantAuthentication,
            subscription=self._generate_subscription(
                name=name, amount=total_amount, schedule=schedule
            ),
        )
        controller = ARBCreateSubscriptionController(request)
        controller.execute()
        response: ARBCreateSubscriptionResponse = controller.getresponse()

        if response.messages.resultCode != "Ok":
            raise ValueError(
                f"Failed to properly create Terminus subscription: {response.messages.message[0]["text"].text}"
            )
        self.profile.authorizenet_payment_id = str(response.customerPaymentProfileId)
        self.profile.save()
