from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase, override_settings
from wialon.api import WialonError

from terminusgps.wialon import (
    WialonSession,
    get_command_name,
    get_unit_by_imei,
    session_is_active,
)


@override_settings(WIALON_TOKEN="super_secure_token")
class WialonSessionTestCase(TestCase):
    def test_no_token_provided_uses_wialon_token_setting(self):
        """Fails if opening a Wialon session without an explicit token fails to use the token provided by settings."""
        session = WialonSession(token=None)
        self.assertEqual(session._token, settings.WIALON_TOKEN)

    def test_token_provided_overrides_wialon_token_setting(self):
        """Fails if opening a Wialon session with an explicit token instead sets the token provided in settings."""
        session = WialonSession(token="another_secure_token")
        self.assertNotEqual(session._token, settings.WIALON_TOKEN)


class SessionIsActiveTestCase(TestCase):
    def test_wialonerror_code_1_returns_false(self):
        """Fails if :py:exec:`~wialon.api.WialonError` was raised with code 1 and :py:obj:`False` wasn't returned."""
        mock_session = MagicMock(WialonSession)
        mock_error = WialonError(1, "Invalid/expired session")
        mock_session.wialon_api.avl_evts.side_effect = mock_error
        self.assertFalse(session_is_active(mock_session))

    def test_wialonerror_non_code_1_reraised(self):
        """Fails if :py:exec:`~wialon.api.WialonError` without code 1 wasn't re-raised."""
        mock_session = MagicMock(WialonSession)
        mock_error = WialonError(6, "Unknown error")
        mock_session.wialon_api.avl_evts.side_effect = mock_error
        with self.assertRaises(WialonError):
            session_is_active(mock_session)

    def test_valid_session_returns_true(self):
        """Fails if a valid session returns anything other than :py:obj:`True`."""
        mock_session = MagicMock(WialonSession)
        mock_session.wialon_api.avl_evts.return_value = {"tm": 0, "events": []}
        self.assertTrue(session_is_active(mock_session))


class GetUnitByImeiTestCase(TestCase):
    def test_multiple_units_found_raises_wialonerror(self):
        """Fails if :py:exec:`~wialon.api.WialonError` wasn't raised when the imei pointed to multiple units."""
        mock_session = MagicMock(WialonSession)
        mock_response = {"totalItemsCount": 2, "items": [{"id": 1}, {"id": 2}]}
        mock_session.wialon_api.core_search_items.return_value = mock_response
        with self.assertRaises(WialonError):
            get_unit_by_imei(mock_session, 12345678)

    def test_single_unit_found(self):
        """Fails if the imei pointed to one unit and it wasn't returned."""
        mock_session = MagicMock(WialonSession)
        mock_response = {"totalItemsCount": 1, "items": [{"id": 1}]}
        mock_session.wialon_api.core_search_items.return_value = mock_response
        result = get_unit_by_imei(mock_session, 12345678)
        self.assertEqual(result["id"], 1)


class GetCommandNameTestCase(TestCase):
    def test_valid_command(self):
        """Fails if the function doesn't return the command's name."""
        mock_session = MagicMock(WialonSession)
        with patch(
            "terminusgps.wialon.get_command_definition_data",
            return_value=[{"id": 1, "n": "Test Command"}],
        ):
            result = get_command_name(mock_session, 12345678, 1)
            self.assertEqual(result, "Test Command")

    def test_unit_without_commands_returns_none(self):
        """Fails if a unit with zero commands returns anything other than :py:obj:`None`."""
        mock_session = MagicMock(WialonSession)
        with patch(
            "terminusgps.wialon.get_command_definition_data", return_value=[]
        ):
            self.assertIsNone(get_command_name(mock_session, 12345678, 1))

    def test_multiple_commands_returns_none(self):
        """Fails if multiple commands were retrieved and the function didn't return :py:obj:`None`."""
        mock_session = MagicMock(WialonSession)
        with patch(
            "terminusgps.wialon.get_command_definition_data",
            return_value=[
                {"id": 1, "n": "Test Command"},
                {"id": 2, "n": "Test Command #2"},
            ],
        ):
            self.assertIsNone(get_command_name(mock_session, 12345678, 1))
