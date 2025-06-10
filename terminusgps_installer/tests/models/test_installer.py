from django.contrib.auth import get_user_model
from django.test import TestCase

from terminusgps_installer.models import Installer


class InstallerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.test_user = get_user_model().objects.create_user(
            first_name="Test",
            last_name="User",
            username="test_user@domain.com",
            email="test_user@domain.com",
            password="test_user_password1!",
        )
        cls.test_installer = Installer.objects.create(user=cls.test_user)

    def tearDown(self) -> None:
        self.test_user.delete()

    def test_installer_str(self) -> None:
        self.assertEqual(str(self.test_installer), "test_user@domain.com")
