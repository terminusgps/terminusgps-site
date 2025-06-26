from authorizenet.constants import constants
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.test.utils import override_settings
from terminusgps.authorizenet.profiles import CustomerProfile

from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    Subscription,
)


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=constants.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE="testMode",
)
class ProtectedCustomerViewTestCase(TestCase):
    def setUp(self) -> None:
        self.test_user_username = "test_user@domain.com"
        self.test_user_email = self.test_user_username
        self.test_user_password = "test_password1!"
        self.test_user_first_name = "TestFirst"
        self.test_user_last_name = "TestLast"
        self.test_user = get_user_model().objects.create_user(
            username=self.test_user_username,
            email=self.test_user_email,
            password=self.test_user_password,
            first_name=self.test_user_first_name,
            last_name=self.test_user_last_name,
        )

    def tearDown(self) -> None:
        self.test_user.delete()

    def test_dashboard_view_protected(self) -> None:
        """Fails if the dashboard view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/")

    def test_account_view_protected(self) -> None:
        """Fails if the account view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/account/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/account/")

    def test_subscription_view_protected(self) -> None:
        """Fails if the subscription view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/subscription/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/subscription/")

    def test_units_view_protected(self) -> None:
        """Fails if the units view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/units/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/units/")

    def test_login(self) -> None:
        """Fails if the test user cannot retrieve the dashboard view after authentication."""
        client = Client()
        client.login(
            username=self.test_user_username, password=self.test_user_password
        )
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_payment_method_view_protected(self) -> None:
        test_customer_profile = CustomerProfile(
            email=self.test_user_email, merchant_id=str(self.test_user.pk)
        )
        test_customer = Customer.objects.create(
            id=test_customer_profile.create(), user=self.test_user
        )
        test_payment_method = CustomerPaymentMethod.objects.create(
            id=1234, customer=test_customer
        )

        client = Client()
        response = client.get(
            f"/payments/{self.test_user.pk}/{test_payment_method.pk}/"
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/login/?next=/payments/{self.test_user.pk}/{test_payment_method.pk}/",
        )
        test_customer_profile.delete()
        test_customer.delete()


class SubscriptionCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        # Create a user and login
        self.test_user_username = "test_user@domain.com"
        self.test_user_email = self.test_user_username
        self.test_user_password = "test_password1!"
        self.test_user_first_name = "TestFirst"
        self.test_user_last_name = "TestLast"
        self.test_user = get_user_model().objects.create_user(
            username=self.test_user_username,
            email=self.test_user_email,
            password=self.test_user_password,
            first_name=self.test_user_first_name,
            last_name=self.test_user_last_name,
        )
        self.client = Client()
        self.client.login(
            username=self.test_user_username, password=self.test_user_password
        )

    def tearDown(self) -> None:
        self.test_user.delete()

    def test_cannot_create_subscription_without_units(self) -> None:
        """Fails if a subscription is created without customer units."""
        test_customer_profile = CustomerProfile(
            email=self.test_user_email, merchant_id=str(self.test_user.pk)
        )
        test_customer = Customer.objects.create(
            user=self.test_user,
            authorizenet_profile_id=test_customer_profile.create(),
        )
        self.client.post(
            f"/payments/{test_customer.pk}/new/",
            {
                "first_name": self.test_user_first_name,
                "last_name": self.test_user_last_name,
                "phone": "555-555-5555",
                "credit_card_number": "4111111111111111",
                "credit_card_expiry_month": "04",
                "credit_card_expiry_year": "39",
                "credit_card_ccv": "444",
                "address_street": "123 Main St",
                "address_city": "Houston",
                "address_state": "Texas",
                "address_country": "USA",
                "address_zip": "77433",
                "default": True,
                "create_shipping_address": True,
            },
        )
        test_customer.refresh_from_db(fields=["payments", "addresses"])
        self.client.post(
            **{
                "path": f"/subscription/{test_customer.pk}/new/",
                "data": {
                    "payment": test_customer.payments.first().pk,
                    "address": test_customer.addresses.first().pk,
                },
            }
        )
        test_customer.refresh_from_db(fields=["subscription", "units"])
        self.assertEqual(test_customer.units.count(), 0)
        with self.assertRaises(Subscription.DoesNotExist):
            getattr(test_customer, "subscription")

        test_customer_profile.id = test_customer.authorizenet_profile_id
        test_customer_profile.delete()
        test_customer.delete()
