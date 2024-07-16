from django.test import TestCase

from terminusgps_tracker.models.forms import RegistrationForm

class RegistrationFormTestCase(TestCase):
    def setUp(self):
        self.form_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@domain.com",
            "wialon_password": "AppleSauce1@!",
            "asset_name": "Test's Ride",
            "imei_number": "123",
        }

    def test_valid_form(self) -> None:
        form_data = self.form_data.copy()
        form = RegistrationForm(form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self) -> None:
        form_data = self.form_data.copy()
        form_data["email"] = ""
        form = RegistrationForm(form_data)
        self.assertFalse(form.is_valid())
