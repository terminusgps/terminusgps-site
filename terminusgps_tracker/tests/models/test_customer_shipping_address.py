from authorizenet import apicontractsv1
from authorizenet.constants import constants
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from terminusgps.authorizenet.constants import ANET_XMLNS
from terminusgps.authorizenet.profiles import AddressProfile, CustomerProfile

from terminusgps_tracker.models import Customer, CustomerShippingAddress


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=constants.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE="testMode",
)
class CustomerShippingAddressTestCase(TestCase):
    def setUp(self) -> None:
        self.test_address_obj = apicontractsv1.customerAddressType(
            firstName="Test",
            lastName="User",
            address="123 Main St",
            city="Houston",
            state="TX",
            zip="77065",
            country="USA",
        )
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
        test_authorizenet_customer_profile_id = (
            test_authorizenet_customer_profile.create()
        )
        test_authorizenet_address_profile = AddressProfile(
            customer_profile_id=test_authorizenet_customer_profile_id, id=None
        )

        self.test_customer = Customer.objects.create(
            user=self.test_user,
            authorizenet_profile_id=test_authorizenet_customer_profile_id,
        )
        self.test_customer_shipping_address = (
            CustomerShippingAddress.objects.create(
                id=test_authorizenet_address_profile.create(
                    address=self.test_address_obj
                ),
                default=False,
                customer=self.test_customer,
            )
        )

    def tearDown(self) -> None:
        self.test_customer.authorizenet_get_customer_profile().delete()
        self.test_user.delete()

    def test_authorizenet_get_profile(self) -> None:
        street = str(
            self.test_customer_shipping_address.authorizenet_get_profile()
            .find(f"{ANET_XMLNS}address")
            .find(f"{ANET_XMLNS}address")
            .text
        )
        self.assertEqual(street, "123 Main St")

    def test_get_absolute_url(self) -> None:
        self.assertEqual(
            self.test_customer_shipping_address.get_absolute_url(),
            reverse(
                "tracker:address detail",
                kwargs={"pk": self.test_customer_shipping_address.pk},
            ),
        )
