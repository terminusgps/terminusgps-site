from urllib.parse import unquote, urljoin

from authorizenet import apicontractsv1
from authorizenet.constants import constants
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from terminusgps.authorizenet.profiles import (
    AddressProfile,
    CustomerProfile,
    PaymentProfile,
)

from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
)


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=constants.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE="testMode",
)
class ProtectedCustomerViewTestCase(StaticLiveServerTestCase):
    fixtures = [
        "terminusgps_tracker/terminusgps/subscription-features.json",
        "terminusgps_tracker/terminusgps/subscription-tiers.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.test_user_id = 9999
        self.test_user_first_name = "Test"
        self.test_user_last_name = "User"
        self.test_user_username = "test_user@domain.com"
        self.test_user_email = self.test_user_username
        self.test_user_password = "test_user_password1!"
        self.test_unit_name = "Test Unit"
        self.test_unit_id = 12345678
        self.test_unit_imei = 1234567890123

        self.test_credit_card_number = 4111111111111111
        self.test_credit_card_expiry_date = "04-2049"
        self.test_credit_card_code = 444

        self.test_address_first_name = self.test_user_first_name
        self.test_address_last_name = self.test_user_last_name
        self.test_address_street = "123 Main St"
        self.test_address_city = "Houston"
        self.test_address_state = "TX"
        self.test_address_country = "USA"
        self.test_address_zip = 77065

        self.test_payment_obj = apicontractsv1.paymentType(
            creditCard=apicontractsv1.creditCardType(
                cardNumber=str(self.test_credit_card_number),
                expirationDate=self.test_credit_card_expiry_date,
                cardCode=str(self.test_credit_card_code),
            )
        )
        self.test_address_obj = apicontractsv1.customerAddressType(
            firstName=self.test_address_first_name,
            lastName=self.test_address_last_name,
            address=self.test_address_street,
            city=self.test_address_city,
            state=self.test_address_state,
            country=self.test_address_country,
            zip=str(self.test_address_zip),
        )

        self.test_user = get_user_model().objects.create_user(
            id=self.test_user_id,
            first_name=self.test_user_first_name,
            last_name=self.test_user_last_name,
            username=self.test_user_username,
            email=self.test_user_email,
            password=self.test_user_password,
        )

        # Create test authorizenet customer profile
        test_customer_profile = CustomerProfile(
            id=None,
            merchant_id=str(self.test_user.pk),
            email=self.test_user.email,
        )
        test_customer_profile_id = test_customer_profile.create()
        # Create test customer
        self.test_customer = Customer.objects.create(
            user=self.test_user,
            authorizenet_profile_id=test_customer_profile_id,
        )

        # Create test authorizenet payment profile
        test_payment_profile = PaymentProfile(
            customer_profile_id=str(
                self.test_customer.authorizenet_profile_id
            ),
            id=None,
        )
        # Create test payment method
        self.test_payment_method = CustomerPaymentMethod.objects.create(
            id=test_payment_profile.create(
                payment=self.test_payment_obj, address=self.test_address_obj
            ),
            customer=self.test_customer,
        )

        # Create test authorizenet address profile
        test_address_profile = AddressProfile(
            customer_profile_id=str(
                self.test_customer.authorizenet_profile_id
            ),
            id=None,
        )
        # Create test shipping address
        self.test_shipping_address = CustomerShippingAddress.objects.create(
            id=test_address_profile.create(address=self.test_address_obj),
            customer=self.test_customer,
        )

        # Get login page
        self.selenium.get(urljoin(self.live_server_url, reverse("login")))
        # Enter username
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys(self.test_user_username)
        # Enter password
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys(self.test_user_password)
        # Click login
        self.selenium.find_element(By.XPATH, "//input[@value='Login']").click()
        # Wait for dashboard response
        wait = WebDriverWait(self.selenium, 4)
        wait.until(lambda d: d.find_element(By.ID, "greeting"))

    def tearDown(self) -> None:
        self.test_customer.authorizenet_get_customer_profile().delete()
        self.test_user.delete()

    def test_customer_account_view_renders_payment_methods(self) -> None:
        """Fails if the customer account view doesn't render the test payment method."""
        target_url = urljoin(self.live_server_url, reverse("tracker:account"))
        self.selenium.get(target_url)
        wait = WebDriverWait(self.selenium, 2)
        wait.until(lambda d: d.find_element(By.ID, "payments"))
        wait = WebDriverWait(self.selenium, 4)
        wait.until(
            lambda d: d.find_element(
                By.ID, f"payment-{self.test_payment_method.pk}"
            )
        )

    def test_customer_account_view_renders_shipping_addresses(self) -> None:
        """Fails if the customer account view doesn't render the test shipping address."""
        target_url = urljoin(self.live_server_url, reverse("tracker:account"))
        self.selenium.get(target_url)

        wait = WebDriverWait(self.selenium, 2)
        wait.until(lambda d: d.find_element(By.ID, "addresses"))
        wait = WebDriverWait(self.selenium, 4)
        wait.until(
            lambda d: d.find_element(
                By.ID, f"address-{self.test_shipping_address.pk}"
            )
        )

    def test_customer_subscription_create_view_payment_method_choices(
        self,
    ) -> None:
        """Fails if the subscription creation view doesn't properly retrieve the test payment method."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:subscription create")
        )
        self.selenium.get(target_url)

        wait = WebDriverWait(self.selenium, 2)
        wait.until(lambda d: d.find_element(By.NAME, "payment"))
        self.assertEqual(
            self.selenium.find_element(
                By.XPATH, f"//option[@value='{self.test_payment_method.pk}']"
            ).text,
            "Visa ending in 1111",
        )

    def test_customer_subscription_create_view_shipping_address_choices(
        self,
    ) -> None:
        """Fails if the subscription creation view doesn't properly retrieve the test shipping address."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:subscription create")
        )
        self.selenium.get(target_url)

        wait = WebDriverWait(self.selenium, 2)
        wait.until(lambda d: d.find_element(By.NAME, "address"))
        self.assertEqual(
            self.selenium.find_element(
                By.XPATH, f"//option[@value='{self.test_shipping_address.pk}']"
            ).text,
            self.test_address_street,
        )


@override_settings(
    MERCHANT_AUTH_ENVIRONMENT=constants.SANDBOX,
    MERCHANT_AUTH_VALIDATION_MODE="testMode",
)
class CustomerViewTestCase(StaticLiveServerTestCase):
    fixtures = [
        "terminusgps_tracker/terminusgps/subscription-features.json",
        "terminusgps_tracker/terminusgps/subscription-tiers.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.test_user_id = 9999
        self.test_user_first_name = "Test"
        self.test_user_last_name = "User"
        self.test_user_username = "test_user@domain.com"
        self.test_user_email = self.test_user_username
        self.test_user_password = "test_user_password1!"

        self.test_user = get_user_model().objects.create_user(
            id=self.test_user_id,
            first_name=self.test_user_first_name,
            last_name=self.test_user_last_name,
            username=self.test_user_username,
            email=self.test_user_email,
            password=self.test_user_password,
        )
        test_customer_profile = CustomerProfile(
            id=None,
            email=self.test_user_email,
            merchant_id=str(self.test_user_id),
        )
        self.test_customer = Customer.objects.create(
            user=self.test_user,
            authorizenet_profile_id=test_customer_profile.create(),
        )

    def tearDown(self) -> None:
        self.test_customer.authorizenet_get_customer_profile().delete()
        self.test_user.delete()

    def test_login(self):
        """Fails if a user wasn't authenticated through the login view."""
        # retrieve login page
        login_url = urljoin(self.live_server_url, reverse("login"))
        self.selenium.get(login_url)
        self.assertEqual(self.selenium.current_url, login_url)

        # input username
        username_input = self.selenium.find_element(By.NAME, "username")
        username_input.send_keys(self.test_user_username)

        # input password
        password_input = self.selenium.find_element(By.NAME, "password")
        password_input.send_keys(self.test_user_password)

        # submit the form
        self.selenium.find_element(By.XPATH, "//input[@value='Login']").click()
        wait = WebDriverWait(self.selenium, 4)
        wait.until(lambda d: d.find_element(By.ID, "greeting"))

        # verify client was redirected to dashboard
        dashboard_url = urljoin(
            self.live_server_url, reverse("tracker:dashboard")
        )
        self.assertEqual(self.selenium.current_url, dashboard_url)

    def test_customer_account_view_protected(self):
        """Fails if the customer account view was retrieved for an anonymous user."""
        target_url = urljoin(self.live_server_url, reverse("tracker:account"))
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse("login", query={"next": reverse("tracker:account")})
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_units_view_protected(self):
        """Fails if the customer units view was retrieved for an anonymous user."""
        target_url = urljoin(self.live_server_url, reverse("tracker:units"))
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse("login", query={"next": reverse("tracker:units")})
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_transactions_view_protected(self):
        """Fails if the customer transactions view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:transactions")
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login", query={"next": reverse("tracker:transactions")}
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_subscription_view_protected(self):
        """Fails if the customer subscription view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:subscription")
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login", query={"next": reverse("tracker:subscription")}
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_payment_method_create_view_protected(self):
        """Fails if the payment method create view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:payment create")
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login", query={"next": reverse("tracker:payment create")}
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_payment_method_detail_view_protected(self):
        """Fails if the payment method detail view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url,
            reverse("tracker:payment detail", kwargs={"pk": 1}),
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login",
                    query={
                        "next": reverse(
                            "tracker:payment detail", kwargs={"pk": 1}
                        )
                    },
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_payment_method_delete_view_protected(self):
        """Fails if the payment method delete view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url,
            reverse("tracker:payment delete", kwargs={"pk": 1}),
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login",
                    query={
                        "next": reverse(
                            "tracker:payment delete", kwargs={"pk": 1}
                        )
                    },
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_payment_method_list_view_protected(self):
        """Fails if the customer payment method list view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:payment list")
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login", query={"next": reverse("tracker:payment list")}
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_shipping_address_create_view_protected(self):
        """Fails if the customer shipping address create view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:address create")
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login", query={"next": reverse("tracker:address create")}
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_shipping_address_detail_view_protected(self):
        """Fails if the customer shipping address detail view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url,
            reverse("tracker:address detail", kwargs={"pk": 1}),
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login",
                    query={
                        "next": reverse(
                            "tracker:address detail", kwargs={"pk": 1}
                        )
                    },
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_shipping_address_delete_view_protected(self):
        """Fails if the customer shipping address delete view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url,
            reverse("tracker:address delete", kwargs={"pk": 1}),
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login",
                    query={
                        "next": reverse(
                            "tracker:address delete", kwargs={"pk": 1}
                        )
                    },
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)

    def test_customer_shipping_address_list_view_protected(self):
        """Fails if the customer shipping address list view was retrieved for an anonymous user."""
        target_url = urljoin(
            self.live_server_url, reverse("tracker:address list")
        )
        expected_url = urljoin(
            self.live_server_url,
            unquote(
                reverse(
                    "login", query={"next": reverse("tracker:address list")}
                )
            ),
        )

        self.selenium.get(target_url)
        self.assertNotEqual(self.selenium.current_url, target_url)
        self.assertEqual(self.selenium.current_url, expected_url)
