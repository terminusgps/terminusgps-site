from unittest import mock

from django.core.validators import ValidationError
from django.test import TestCase
from wialon.api import WialonError

from terminusgps.wialon import WialonSession
from terminusgps_installer.validators import validate_imei, validate_is_digit


class ValidateImeiTestCase(TestCase):
    def test_multiple_units_found_raises_validationerror(self):
        """Fails if the IMEI number pointed to multiple units and :py:exec:`~django.core.exceptions.ValidationError` wasn't raised."""
        test_imei = "1234567890"
        with mock.patch(
            "terminusgps_installer.validators.get_session",
            return_value=mock.MagicMock(WialonSession),
        ):
            with mock.patch(
                "terminusgps_installer.validators.get_unit_by_imei",
                side_effect=WialonError(
                    -1, f"Too many items returned for IMEI #: {test_imei}"
                ),
            ):
                with self.assertRaises(ValidationError):
                    validate_imei(test_imei)

    def test_wialonerror_raises_validationerror(self):
        """Fails if :py:exec:`~django.core.exceptions.ValidationError` wasn't raised when :py:exec:`~wialon.api.WialonError` was."""
        test_imei = "1234567890"
        with mock.patch(
            "terminusgps_installer.validators.get_session",
            return_value=mock.MagicMock(WialonSession),
        ):
            with mock.patch(
                "terminusgps_installer.validators.get_unit_by_imei",
                side_effect=WialonError(6, "Unknown Error"),
            ):
                with self.assertRaises(ValidationError):
                    validate_imei(test_imei)

    def test_valid_imei(self):
        """Fails if a valid IMEI number doesn't pass the validator."""
        test_imei = "1234567890"
        with mock.patch(
            "terminusgps_installer.validators.get_session",
            return_value=mock.MagicMock(WialonSession),
        ):
            with mock.patch(
                "terminusgps_installer.validators.get_unit_by_imei",
                return_value={"id": 12345678, "nm": "Test Unit"},
            ):
                validate_imei(test_imei)


class ValidateIsDigitTestCase(TestCase):
    def test_non_digit_raises_validationerror(self):
        """Fails if a value containing non-digits doesn't raise :py:exec:`~django.core.exceptions.ValidationError`."""
        with self.assertRaises(ValidationError):
            validate_is_digit("123456789a")

    def test_all_digits_passes(self):
        """Fails if a value containing only digits doesn't pass the validator."""
        validate_is_digit("1234567890")
