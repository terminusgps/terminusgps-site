from authorizenet.apicontractsv1 import (
    createCustomerShippingAddressRequest,
    createCustomerShippingAddressResponse,
    customerAddressType,
    paymentProfile,
    paymentType,
)
from authorizenet.apicontrollers import (
    createCustomerPaymentProfileController,
    createCustomerShippingAddressController,
)

from terminusgps_tracker.authorizenetapi.auth import get_merchant_auth


def create_customer_address(
    profile_id: str, address: customerAddressType, default: bool = True
) -> str:
    request = createCustomerShippingAddressRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=profile_id,
        address=address,
        defaultShippingAddress=default,
    )
    controller = createCustomerShippingAddressController(request)
    controller.execute()
    response: createCustomerShippingAddressResponse = controller.execute()
    if response.messages.resultCode != "Ok":
        raise ValueError(
            f"Failed to create profile in AuthorizeNET: {response.messages.message["text"].text}"
        )
    return response.customerAddressId


def create_customer_payment_profile(
    profile_id: str,
    payment: paymentType,
    address: customerAddressType,
    default: bool = True,
) -> str:
    payment_profile = paymentProfile(billTo=address, payment=payment)
    request = createCustomerShippingAddressRequest(
        merchantAuthentication=get_merchant_auth(),
        customerProfileId=profile_id,
        paymentProfile=payment_profile,
        defaultPaymentProfile=default,
    )
    controller = createCustomerPaymentProfileController(request)
    controller.execute()
    response: createCustomerPaymentProfileRequest = controller.execute()
    if response.messages.resultCode != "Ok":
        raise ValueError(
            f"Failed to create payment profile in AuthorizeNET: {response.messages.message["text"].text}"
        )
    return response.customerPaymentProfileId
