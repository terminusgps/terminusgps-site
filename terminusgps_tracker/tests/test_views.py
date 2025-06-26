from authorizenet.constants import constants
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.test.utils import override_settings
from terminusgps.authorizenet.profiles import CustomerProfile

from terminusgps_tracker.models import Customer


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=constants.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE="testMode",
)
class CustomerViewTestCase(TestCase):
    def setUp(self) -> None:
        self.test_user_username = "test_user@domain.com"
        self.test_user_email = self.test_user_username
        self.test_user_password = "test_password1!"

        self.test_user = get_user_model().objects.create_user(
            username=self.test_user_username,
            email=self.test_user_email,
            password=self.test_user_password,
        )
        test_customer_profile = CustomerProfile(
            email=self.test_user_email, merchant_id=str(self.test_user.pk)
        )
        self.test_customer = Customer.objects.create(
            user=self.test_user,
            authorizenet_profile_id=test_customer_profile.create(),
        )

    def tearDown(self) -> None:
        CustomerProfile(
            id=self.test_customer.authorizenet_profile_id,
            email=self.test_customer.user.email,
            merchant_id=str(self.test_customer.user.pk),
        ).delete()
        self.test_customer.delete()

    def test_dashboard_view_protected(self) -> None:
        """Fails if the dashboard view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_account_view_protected(self) -> None:
        """Fails if the account view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/account/")
        self.assertEqual(response.status_code, 302)

    def test_subscription_view_protected(self) -> None:
        """Fails if the subscription view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/subscription/")
        self.assertEqual(response.status_code, 302)

    def test_units_view_protected(self) -> None:
        """Fails if the units view was accessed by an anonymous user."""
        client = Client()
        response = client.get("/units/")
        self.assertEqual(response.status_code, 302)

    def test_login(self) -> None:
        """Fails if a user cannot properly authenticate through the login view."""
        client = Client()
        client.login(
            username=self.test_user_username, password=self.test_user_password
        )
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
