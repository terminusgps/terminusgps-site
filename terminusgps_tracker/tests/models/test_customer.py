from authorizenet import apicontractsv1
from authorizenet.constants import constants
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)

from terminusgps_tracker.models import Customer


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=constants.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE="testMode",
)
class CustomerTestCase(TestCase):
    def setUp(self) -> None:
        self.test_user = get_user_model().objects.create_user(
            id=9999,
            username="test_user@domain.com",
            email="test_user@domain.com",
            password="test_user_password",
            first_name="Test",
            last_name="User",
        )
        test_authorizenet_customer_profile = CustomerProfile(
            id=None,
            email=self.test_user.email,
            merchant_id=str(self.test_user.pk),
        )
        self.test_customer = Customer.objects.create(
            user=self.test_user,
            authorizenet_profile_id=test_authorizenet_customer_profile.create(),
        )

    def tearDown(self) -> None:
        self.test_customer.authorizenet_get_customer_profile().delete()
        self.test_user.delete()

    def test_customer_authorizenet_get_customer_profile(self) -> None:
        control_authorizenet_customer_profile = CustomerProfile(
            id=str(self.test_customer.authorizenet_profile_id),
            email=str(self.test_customer.user.email),
            merchant_id=str(self.test_customer.user.pk),
        )
        test_authorizenet_customer_profile = (
            self.test_customer.authorizenet_get_customer_profile()
        )
        self.assertEqual(
            control_authorizenet_customer_profile.id,
            test_authorizenet_customer_profile.id,
        )
        self.assertEqual(
            control_authorizenet_customer_profile.email,
            test_authorizenet_customer_profile.email,
        )
        self.assertEqual(
            control_authorizenet_customer_profile.merchant_id,
            test_authorizenet_customer_profile.merchant_id,
        )

    def test_customer_authorizenet_sync_payment_profiles(self) -> None:
        test_payment_obj = apicontractsv1.paymentType(
            creditCard=apicontractsv1.creditCardType(
                cardNumber="4111111111111111",
                expirationDate="04-2049",
                cardCode="444",
            )
        )
        test_address_obj = apicontractsv1.customerAddressType(
            firstName="Test",
            lastName="User",
            address="123 Main St",
            city="Houston",
            state="TX",
            zip="77065",
            country="USA",
        )
        test_payment_profile = PaymentProfile(
            id=None,
            customer_profile_id=self.test_customer.authorizenet_profile_id,
        )
        # Create a payment profile in Authorizenet
        test_payment_profile_id = test_payment_profile.create(
            address=test_address_obj, payment=test_payment_obj
        )

        # Retrieve payments from Authorizenet and create payment methods
        self.test_customer.authorizenet_sync_payment_profiles()
        self.assertEqual(
            test_payment_profile_id, self.test_customer.payments.first().pk
        )

    def test_customer_authorizenet_sync_address_profiles(self) -> None:
        test_address_obj = apicontractsv1.customerAddressType(
            firstName="Test",
            lastName="User",
            address="123 Main St",
            city="Houston",
            state="TX",
            zip="77065",
            country="USA",
        )
        test_address_profile = AddressProfile(
            id=None,
            customer_profile_id=self.test_customer.authorizenet_profile_id,
        )
        test_address_profile_id = test_address_profile.create(
            address=test_address_obj
        )

        # Retrieve addresses from Authorizenet and create shipping addresses
        self.test_customer.authorizenet_sync_address_profiles()
        self.assertEqual(
            test_address_profile_id, self.test_customer.addresses.first().pk
        )
