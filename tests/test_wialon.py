import random
import string
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.test import TestCase
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


@pytest.fixture(autouse=True)
def use_default_wialon_token(settings):
    settings.WIALON_TOKEN = "super_secure_token"


@pytest.fixture
def mock_api():
    with patch("terminusgps.wialon.Wialon") as mock_wialon_cls:
        mock_api = MagicMock()
        mock_api.token_login.return_value = {
            "eid": "abc123",
            "au": "test",
            "user": {"id": 1},
            "gis_sid": "def456",
        }
        mock_wialon_cls.return_value = mock_api
        yield mock_api


def test_wialonsession_no_token_provided_uses_wialon_token_setting(mock_api):
    session = WialonSession(token=None)
    assert session._token == settings.WIALON_TOKEN


def test_wialonsession_explicit_token_overrides_wialon_token_setting(mock_api):
    expected_token = "another_secure_token"
    session = WialonSession(token=expected_token)
    session.login()
    assert session._token == expected_token
    assert session._token != settings.WIALON_TOKEN


def test_wialonsession_login(mock_api):
    session = WialonSession()
    session.login()
    assert session.wialon_api.sid == "abc123"
    assert session._uid == 1
    assert session._username == "test"
    assert session._gis_sid == "def456"


def test_wialonsession_login_with_username(mock_api):
    mock_api.token_login.return_value = {
        "eid": "abc123",
        "au": "test_user",
        "user": {"id": 1},
        "gis_sid": "def456",
    }
    session = WialonSession()
    session.login(username="test_user")
    assert session._uid == 1
    assert session._username == "test_user"
    assert session._gis_sid == "def456"
    assert session.id == "abc123"


def test_wialonsession_logout(mock_api):
    session = WialonSession()
    session.login()
    mock_api.core_logout.return_value = {"error": 0}
    session.logout()
    assert session.id is None


def test_wialonsession_logout_error_raises_wialonerror(mock_api):
    session = WialonSession()
    session.login()
    mock_api.core_logout.return_value = {"error": 1}
    with pytest.raises(WialonError):
        session.logout()


@pytest.mark.parametrize(
    "token_login_response",
    [
        {
            "eid": "abc123",
            "au": "test_user_abc",
            "user": {"id": 1},
            "gis_sid": "123",
        },
        {
            "eid": "def123",
            "au": "test_user_def",
            "user": {"id": 2},
            "gis_sid": "123",
        },
        {
            "eid": "ghi123",
            "au": "test_user_ghi",
            "user": {"id": 3},
            "gis_sid": "123",
        },
        {
            "eid": "jkl123",
            "au": "test_user_jkl",
            "user": {"id": 4},
            "gis_sid": "123",
        },
        {
            "eid": "mno123",
            "au": "test_user_mno",
            "user": {"id": 5},
            "gis_sid": "123",
        },
        {
            "eid": "pqr123",
            "au": "test_user_pqr",
            "user": {"id": 6},
            "gis_sid": "123",
        },
    ],
)
def test_wialonsession_public_attributes(mock_api, token_login_response):
    """Fails if required attributes weren't set after successfully logging into a Wialon API session."""
    mock_api.token_login.return_value = token_login_response
    session = WialonSession()
    session.login()
    assert session.wialon_api == mock_api
    assert session.uid == token_login_response["user"]["id"]
    assert session.username == token_login_response["au"]
    assert session.id == token_login_response["eid"]
    assert session.gis_sid == token_login_response["gis_sid"]


def test_wialonsession_exit(mock_api):
    """Fails if :py:meth:`__exit__` didn't logout of the Wialon API session."""
    session = WialonSession()
    session.login()
    mock_api.core_logout.return_value = {"error": 0}
    session.__exit__("", "", "")
    mock_api.core_logout.assert_called_once()


def test_wialonsession_str(mock_api):
    session = WialonSession()
    session.login()
    assert str(session) == "WialonSession #abc123"


def test_wialonsession_repr(mock_api):
    session = WialonSession()
    session.login()
    assert repr(session) == "WialonSession(sid=abc123)"


@pytest.mark.parametrize(
    "mock_core_search_item_response",
    [
        {"item": {"id": 1, "nm": "Test Resource #1"}},
        {"item": {"id": 2, "nm": "Test Resource #2"}},
        {"item": {"id": 3, "nm": "Test Resource #3"}},
        {"item": {"id": 4, "nm": "Test Resource #4"}},
        {"item": {"id": 5, "nm": ""}},
    ],
)
def test_get_unit_by_id(mock_api, mock_core_search_item_response):
    unit_id = mock_core_search_item_response["item"]["id"]
    unit_name = mock_core_search_item_response["item"]["nm"]
    mock_api.core_search_item.return_value = mock_core_search_item_response
    session = WialonSession()
    session.login()
    result = get_unit_by_id(session, unit_id)
    assert result["id"] == unit_id
    assert result["nm"] == unit_name


@pytest.mark.parametrize(
    "mock_api_response",
    [
        {"totalItemsCount": 0, "items": []},
        {"totalItemsCount": 1, "items": [{"id": 1}]},
        {"totalItemsCount": 2, "items": [{"id": 1}, {"id": 2}]},
    ],
)
def test_get_resources(mock_api, mock_api_response):
    mock_api.core_search_items.return_value = mock_api_response
    session = WialonSession()
    session.login()
    result = get_resources(session)
    assert len(result) == mock_api_response["totalItemsCount"]


@pytest.mark.parametrize(
    "mock_core_search_item_response",
    [
        {"item": {"id": 1, "nm": "Test Resource #1"}},
        {"item": {"id": 2, "nm": "Test Resource #2"}},
        {"item": {"id": 3, "nm": "Test Resource #3"}},
        {"item": {"id": 4, "nm": "Test Resource #4"}},
        {"item": {"id": 5, "nm": ""}},
    ],
)
def test_get_resource(mock_api, mock_core_search_item_response):
    mock_api.core_search_item.return_value = mock_core_search_item_response
    resource_id = mock_core_search_item_response["item"]["id"]
    resource_name = mock_core_search_item_response["item"]["nm"]
    session = WialonSession()
    session.login()
    result = get_resource(session, resource_id)
    assert result["id"] == resource_id
    assert result["nm"] == resource_name


@pytest.mark.parametrize("vin", ["JTHBTHA", "asdfjasdjf"])
def test_get_vin_info(mock_api, vin):
    mock_api.unit_get_vin_info.return_value = {
        "vin_lookup_result": {"pflds": []}
    }
    session = WialonSession()
    session.login()
    result = get_vin_info(session, vin)
    assert result == {"pflds": []}


def test_generate_locator_token(mock_api):
    expected_token = "".join(
        random.choices(string.ascii_letters + string.digits, k=72)
    )
    mock_api.token_update.return_value = {"h": expected_token}
    session = WialonSession()
    session.login()
    result = generate_locator_token(session, [1])
    assert result == expected_token


@pytest.mark.parametrize("token", ["123abc", "456def", ""])
def test_generate_locator_url(mock_api, token):
    result = generate_locator_url(token)
    assert (
        result
        == f"https://hosting.terminusgps.com/locator/index.html?t={token}"
    )


def test_session_is_active_wialonerror_code_1_returns_false(mock_api):
    mock_api.avl_evts.side_effect = WialonError(1, "Invalid/expired session")
    session = WialonSession()
    session.login()
    assert not session_is_active(session)


def test_session_is_active_wialonerror_non_code_1_reraised(mock_api):
    mock_api.avl_evts.side_effect = WialonError(6, "Unknown error")
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        session_is_active(session)


def test_session_is_active_valid_session_returns_true(mock_api):
    mock_api.avl_evts.return_value = {"tm": 0, "events": []}
    session = WialonSession()
    session.login()
    assert session_is_active(session)


def test_get_unit_by_imei_multiple_units_found_raises_wialonerror(mock_api):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 2,
        "items": [{"id": 1}, {"id": 2}],
    }
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        get_unit_by_imei(session, 12345678)


def test_get_unit_by_imei_single_unit_found(mock_api):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1}],
    }
    session = WialonSession()
    session.login()
    result = get_unit_by_imei(session, 12345678)
    assert result["id"] == 1


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
