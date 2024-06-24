from django.contrib.auth.models import User
from django.test import TestCase

from .models import QuickbooksToken, WialonToken


class QuickbooksTokenTestCase(TestCase):
    def test_set_and_retrieve_access_token(self) -> None:
        """Test setting and retrieving access token."""
        unencrypted_access_token = "super_secure_access_token"
        test_user = User.objects.create_user(
            username="test_user",
            password="test_password",
            email="test_user@example.com",
        )
        test_token = QuickbooksToken.objects.create(user=test_user)

        test_token.access_token = unencrypted_access_token

        self.assertEqual(test_token.access_token, unencrypted_access_token)
        self.assertNotEqual(test_token._access_token, unencrypted_access_token)

    def test_set_and_retrieve_refresh_token(self) -> None:
        """Test setting and retrieving refresh token."""
        unencrypted_refresh_token = "super_secure_refresh_token"
        test_user = User.objects.create_user(
            username="test_user",
            password="test_password",
            email="test_user@example.com",
        )
        test_token = QuickbooksToken.objects.create(user=test_user)

        test_token.refresh_token = unencrypted_refresh_token

        self.assertEqual(test_token.refresh_token, unencrypted_refresh_token)
        self.assertNotEqual(test_token._refresh_token, unencrypted_refresh_token)


class QuickbooksAuthorizationTestCase(TestCase):
    def test_authorize_new_user(self) -> None:
        test_user = User.objects.create_user(
            username="test_user",
            password="test_password",
            email="test_user@example.com",
        )
        test_token = QuickbooksToken.objects.create(
            user=test_user,
        )

        self.client.login(username="test_user", password="test_password")


class WialonTokenTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            password="test_password",
            email="test_user@example.com",
        )
        self.token = WialonToken.objects.create(user=self.user)

    def test_set_and_retrieve_access_token(self):
        """Succeeds if an access token can be set and retrieved from :models:`terminusgps_tracker.models.WialonToken`."""
        unencrypted_access_token = "a_very_secure_access_token"

        self.token.access_token = unencrypted_access_token

        self.assertEqual(self.token.access_token, unencrypted_access_token)
        self.assertNotEqual(self.token._access_token, unencrypted_access_token)
