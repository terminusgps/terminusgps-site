from django.test import TestCase
from django.core.exceptions import ValidationError

from terminusgps_tracker.models.forms import RegistrationForm
from terminusgps_tracker.validators import validate_contains_uppercase_letter, validate_contains_lowercase_letter, validate_contains_digit, validate_contains_special_symbol

class ValidatorTestCase(TestCase):
    def setUp(self) -> None:
        self.valid_password = "Password1!"

    def test_validate_contains_uppercase_letter(self) -> None:
        self.assertEqual(validate_contains_uppercase_letter(self.valid_password), self.valid_password)

    def test_validate_contains_lowercase_letter(self) -> None:
        value = "Password1!"
        self.assertEqual(validate_contains_lowercase_letter(value), value)

    def test_validate_contains_digit(self) -> None:
        value = "Password1!"
        self.assertEqual(validate_contains_digit(value), value)

    def test_validate_contains_special_symbol(self) -> None:
        value = "Password1!"
        self.assertEqual(validate_contains_special_symbol(value), value)

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
