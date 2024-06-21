from django.contrib.auth.models import User
from django.test import TestCase

from .models import QuickbooksToken


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
