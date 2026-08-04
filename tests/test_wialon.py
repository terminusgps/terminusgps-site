import random
import string
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import TestCase, override_settings
from wialon.api import WialonError

from terminusgps.wialon import (
    WialonSession,
    generate_locator_token,
    generate_locator_url,
    get_command_name,
    get_resource,
    get_resources,
    get_unit_by_id,
    get_unit_by_imei,
    get_vin_info,
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
        expected_token = "another_secure_token"
        session = WialonSession(token=expected_token)
        self.assertNotEqual(session._token, settings.WIALON_TOKEN)
        self.assertEqual(session._token, expected_token)

    def test_login(self):
        """Fails if :py:meth:`login` doesn't properly login to the Wialon API and save its session id."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            self.assertEqual(session._uid, test_uid)
            self.assertEqual(session._username, test_username)
            self.assertEqual(session._gis_sid, test_gis_sid)
            self.assertEqual(mock_api.sid, test_eid)

    def test_login_with_username(self):
        """Fails if :py:meth:`login` doesn't properly login to the Wialon API and save its session id with an explicit username."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login(username=test_username)
            mock_api.token_login.assert_called_once_with(
                token=test_token, flags=0x3, operateAs=test_username
            )
            self.assertEqual(session._uid, test_uid)
            self.assertEqual(session._username, test_username)
            self.assertEqual(session._gis_sid, test_gis_sid)
            self.assertEqual(mock_api.sid, test_eid)

    def test_logout(self):
        """Fails if :py:meth:`logout` doesn't properly logout of the Wialon API and set its session id to :py:obj:`None`."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_api.core_logout.return_value = {"error": 0}
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            self.assertEqual(session.wialon_api.sid, test_eid)
            session.logout()
            self.assertIsNone(session.wialon_api.sid)

    def test_logout_error(self):
        """Fails if a Wialon API error happened during logout and wasn't reraised."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_api.core_logout.return_value = {"error": 1}
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            self.assertEqual(session.wialon_api.sid, test_eid)
            with self.assertRaises(WialonError):
                session.logout()

    def test_public_attributes(self):
        """Fails if required attributes weren't set after successfully logging in."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            self.assertEqual(session.wialon_api, mock_api)
            self.assertEqual(session.uid, test_uid)
            self.assertEqual(session.username, test_username)
            self.assertEqual(session.id, test_eid)
            self.assertEqual(session.gis_sid, test_gis_sid)

    def test___exit__(self):
        """Fails if :py:meth:`__exit__` didn't call :py:meth:`logout` if required."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_api.core_logout.return_value = {"error": 0}
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            session.__exit__("", "", "")
            mock_api.core_logout.assert_called_once()
            session.__exit__("", "", "")
            mock_api.core_logout.assert_called_once()

    def test___enter__(self):
        """Fails if :py:meth:`__enter__` didn't call :py:meth:`login` if required."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_api.core_logout.return_value = {"error": 0}
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            session.__exit__("", "", "")
            mock_api.core_logout.assert_called_once()
            session.__exit__("", "", "")
            mock_api.core_logout.assert_called_once()

    def test___str__(self):
        """Fails if :py:meth:`__str__` returns unexpected values."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            self.assertEqual(str(session), f"WialonSession #{session.id}")

    def test___repr__(self):
        """Fails if :py:meth:`__repr__` returns unexpected values."""
        with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
            test_eid = "abc123"
            test_uid = 1
            test_username = "test"
            test_user = {"id": test_uid}
            test_gis_sid = "def456"
            test_token = "super_secure_token"
            mock_api = MagicMock()
            mock_api.token_login.return_value = {
                "eid": test_eid,
                "au": test_username,
                "user": test_user,
                "gis_sid": test_gis_sid,
            }
            mock_wialon_cls.return_value = mock_api
            session = WialonSession(token=test_token)
            session.login()
            self.assertEqual(repr(session), f"WialonSession(sid={session.id})")


class GetUnitByIdTestCase(TestCase):
    def test_return_value(self):
        """Fails if the function doesn't return the expected Wialon unit."""
        test_unit_id = 12345678
        test_flags = 42
        test_unit_name = "Test Unit"
        mock_session = MagicMock(WialonSession)
        mock_session.wialon_api.core_search_item.return_value = {
            "item": {"id": test_unit_id, "nm": test_unit_name}
        }
        result = get_unit_by_id(mock_session, test_unit_id, test_flags)
        self.assertEqual(result["id"], test_unit_id)
        self.assertEqual(result["nm"], test_unit_name)


class GetResourcesTestCase(TestCase):
    def test_return_value(self):
        """Fails if the function doesn't return the expected Wialon resources."""
        mock_session = MagicMock(WialonSession)
        mock_response = {"totalItemsCount": 2, "items": [{"id": 1}, {"id": 2}]}
        mock_session.wialon_api.core_search_items.return_value = mock_response
        result = get_resources(mock_session)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[1]["id"], 2)


class GetResourceTestCase(TestCase):
    def test_return_value(self):
        """Fails if the function doesn't return the expected Wialon resource."""
        test_resource_id = 12345678
        test_flags = 42
        test_resource_name = "Test Resource"
        mock_session = MagicMock(WialonSession)
        mock_session.wialon_api.core_search_item.return_value = {
            "item": {"id": test_resource_id, "nm": test_resource_name}
        }
        result = get_resource(mock_session, test_resource_id, test_flags)
        self.assertEqual(result["id"], test_resource_id)
        self.assertEqual(result["nm"], test_resource_name)


class GetVinInfoTestCase(TestCase):
    def test_return_value(self):
        """Fails if the function doesn't return the expected VIN info."""
        test_vin = ""
        mock_session = MagicMock(WialonSession)
        mock_session.wialon_api.unit_get_vin_info.return_value = {
            "vin_lookup_result": {"pflds": []}
        }
        result = get_vin_info(mock_session, test_vin)
        self.assertEqual(result["pflds"], [])


class GenerateLocatorTokenTestCase(TestCase):
    def setUp(self):
        self.generate_test_token = lambda k: "".join(
            random.choices(string.ascii_letters + string.digits, k=k)
        )

    def test_token_returned(self):
        """Fails if the function doesn't return a locator token."""
        expected_token = self.generate_test_token(72)
        expected_unit_ids = [1, 2, 3]
        mock_session = MagicMock(WialonSession)
        mock_session.wialon_api.token_update.return_value = {
            "h": expected_token
        }
        result = generate_locator_token(mock_session, expected_unit_ids)
        self.assertEqual(result, expected_token)


class GenerateLocatorUrlTestCase(TestCase):
    def setUp(self):
        self.generate_test_token = lambda k: "".join(
            random.choices(string.ascii_letters + string.digits, k=k)
        )

    def test_url_returned(self):
        """Fails if the function doesn't reutrn a locator url."""
        expected_token = self.generate_test_token(72)
        expected_url = f"https://hosting.terminusgps.com/locator/index.html?t={expected_token}"
        result = generate_locator_url(expected_token)
        self.assertEqual(result, expected_url)


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
