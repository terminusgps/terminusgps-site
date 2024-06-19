from django.contrib.auth.models import User
from django.test import TestCase

from payments.models import AuthToken, QuickbooksToken


class AuthTokenTestCase(TestCase):
    def test_can_set_and_get_access_token(self):
        """Test whether we can set and get an access token."""
        unencrypted_access_token = "very_secure_access_token"
        user = User.objects.create_user(
            username="test_user",
            email="test_user@domain.com",
            password="test_password",
        )
        token = AuthToken.objects.create(user=user)
        token.access_token = unencrypted_access_token

        self.assertNotEqual(token._access_token, unencrypted_access_token)
        self.assertEqual(token.access_token, unencrypted_access_token)

    def test_can_set_and_get_refresh_token(self):
        """Test whether we can set and get an refresh token."""
        unencrypted_refresh_token = "very_secure_refresh_token"
        user = User.objects.create_user(
            username="test_user",
            email="test_user@domain.com",
            password="test_password",
        )
        token = AuthToken.objects.create(user=user)
        token.refresh_token = unencrypted_refresh_token

        self.assertNotEqual(token._refresh_token, unencrypted_refresh_token)
        self.assertEqual(token.refresh_token, unencrypted_refresh_token)
