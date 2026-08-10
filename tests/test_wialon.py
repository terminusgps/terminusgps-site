from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from wialon.api import WialonError

from terminusgps.constants import CommandFlag, CommandLinkType
from terminusgps.wialon import (
    WialonSession,
    create_account,
    create_resource,
    create_user,
    disable_account,
    enable_account,
    execute_command,
    generate_locator_token,
    generate_locator_url,
    get_command_definition_data,
    get_command_name,
    get_resource,
    get_resource_choices,
    get_resources,
    get_unit_by_id,
    get_unit_by_imei,
    get_vin_info,
    session_is_active,
    update_name,
    update_vin,
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
    """Fails if initializing a Wialon session without a token doesn't set :py:attr:`_token` to :py:obj:`~django.conf.settings.WIALON_TOKEN`."""
    session = WialonSession(token=None)
    assert session._token == settings.WIALON_TOKEN


def test_wialonsession_explicit_token_overrides_wialon_token_setting(mock_api):
    """Fails if initializing a Wialon session with an explicitly provided token doesn't set :py:attr:`_token` to the provided value."""
    expected_token = "another_secure_token"
    session = WialonSession(token=expected_token)
    session.login()
    assert session._token == expected_token


def test_wialonsession_login(mock_api):
    """Fails if :py:meth:`login` doesn't properly set required attributes post login."""
    session = WialonSession()
    session.login()
    assert session.wialon_api.sid == "abc123"
    assert session._uid == 1
    assert session._username == "test"
    assert session._gis_sid == "def456"


def test_wialonsession_login_with_username(mock_api):
    """Fails if :py:meth:`login` doesn't properly set required attributes with an explicitly provided username post login."""
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


def test_wialonsession_logout_sets_id_to_none(mock_api):
    """Fails if :py:meth:`WialonSession.logout` logs out of the Wialon API session but doesn't set :py:attr:`WialonSession.id` to :py:obj:`None`."""
    mock_api.core_logout.return_value = {"error": 0}
    session = WialonSession()
    session.login()
    session.logout()
    assert session.id is None


def test_wialonsession_logout_error_raises_wialonerror(mock_api):
    """Fails if :py:meth:`logout` doesn't raise :py:exec:`wialon.api.WialonError` after logout failure."""
    mock_api.core_logout.return_value = {"error": 1}
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        session.logout()


def test_wialonsession_public_attributes_accessible(mock_api):
    """Fails if a public attribute wasn't accessible after successfully logging into the Wialon session."""
    session = WialonSession()
    session.login()
    assert session.wialon_api == mock_api
    assert session.uid == 1
    assert session.username == "test"
    assert session.id == "abc123"
    assert session.gis_sid == "def456"


def test_wialonsession_str(mock_api):
    """Fails if :py:meth:`WialonSession.__str__` returns an unexpected value."""
    session = WialonSession()
    session.login()
    assert str(session) == "WialonSession #abc123"


def test_wialonsession_repr(mock_api):
    """Fails if :py:meth:`WialonSession.__repr__` returns an unexpected value."""
    session = WialonSession()
    session.login()
    assert repr(session) == "WialonSession(sid=abc123)"


def test_get_unit_by_id(mock_api):
    """Fails if :py:func:`get_unit_by_id` returns unexpected values after a successful Wialon API call."""
    mock_api.core_search_item.return_value = {
        "item": {"id": 1, "nm": "Test Unit"}
    }
    session = WialonSession()
    session.login()
    result = get_unit_by_id(session, 1)
    assert result["id"] == 1
    assert result["nm"] == "Test Unit"


def test_get_unit_by_id_reraises_wialonerror(mock_api):
    """Fails if :py:func:`get_unit_by_id` doesn't re-raise :py:exec:`~wialon.api.WialonError` on Wialon API error."""
    mock_api.core_search_item.side_effect = WialonError(6, "Unknown error")
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        get_unit_by_id(session, 1)


def test_get_resources(mock_api):
    """Fails if :py:func:`get_resources` doesn't return the expected list of Wialon resources."""
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 2,
        "items": [{"id": 1}, {"id": 2}],
    }
    session = WialonSession()
    session.login()
    result = get_resources(session)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2


def test_get_resources_reraises_wialonerror(mock_api):
    """Fails if :py:func:`get_resources` doesn't re-raise :py:exec:`~wialon.api.WialonError` on Wialon API error."""
    mock_api.core_search_items.side_effect = WialonError(6, "Unknown error")
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        get_resources(session)


def test_get_resources_with_no_existing_resources(mock_api):
    """Fails if :py:func:`get_resources` returns anything other than an empty list there are no Wialon resources."""
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 0,
        "items": [],
    }
    session = WialonSession()
    session.login()
    result = get_resources(session)
    assert result == []


def test_get_resource(mock_api):
    mock_api.core_search_item.return_value = {
        "item": {"id": 1, "nm": "Test Resource"}
    }
    session = WialonSession()
    session.login()
    result = get_resource(session, 1)
    assert result["id"] == 1
    assert result["nm"] == "Test Resource"


def test_get_vin_info(mock_api):
    mock_api.unit_get_vin_info.return_value = {
        "vin_lookup_result": {"pflds": []}
    }
    session = WialonSession()
    session.login()
    result = get_vin_info(session, "1HTLDUXR2JH208285")
    assert result == {"pflds": []}


def test_generate_locator_token(mock_api):
    expected_token = "cadwc9GtAKcptXuTOX2oWJCA1Df9R360tWilwUZcoFPqH1SceGGoLET0v8h75nzIuaAEUwqs"
    mock_api.token_update.return_value = {"h": expected_token}
    session = WialonSession()
    session.login()
    result = generate_locator_token(session, unit_ids=[1])
    assert result == expected_token


def test_generate_locator_url(mock_api):
    result = generate_locator_url("123abc")
    assert (
        result == "https://hosting.terminusgps.com/locator/index.html?t=123abc"
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


def test_get_resource_choices(mock_api):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 2,
        "items": [
            {"id": 1, "nm": "Test Resource #1"},
            {"id": 2, "nm": "Test Resource #2"},
        ],
    }
    session = WialonSession()
    session.login()
    result = get_resource_choices(session)
    assert len(result) == 2
    assert result[0][0] == 1
    assert result[0][1] == "Test Resource #1"
    assert result[1][0] == 2
    assert result[1][1] == "Test Resource #2"


def test_create_resource(mock_api):
    mock_api.core_create_resource.return_value = {
        "item": {"id": 1, "nm": "Test Resource"}
    }
    session = WialonSession()
    session.login()
    result = create_resource(
        session,
        creator_id=12345678,
        name="Test Resource",
        skip_creator_check=False,
    )
    assert result == 1


def test_create_resource_reraises_wialonerror(mock_api):
    mock_api.core_create_resource.side_effect = WialonError(6, "Unknown error")
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        create_resource(
            session,
            creator_id=12345678,
            name="Test Resource",
            skip_creator_check=False,
        )


def test_create_user(mock_api):
    mock_api.core_create_user.return_value = {
        "item": {"id": 1, "nm": "Test User"}
    }
    session = WialonSession()
    session.login()
    result = create_user(
        session,
        creator_id=12345678,
        username="Test User",
        password="super_secure_password1!",
    )
    assert result == 1


def test_create_account(mock_api):
    mock_api.account_create_account.return_value = {}
    session = WialonSession()
    session.login()
    result = create_account(
        session, resource_id=1, plan="terminusgps_ext_hist"
    )
    assert result is None


def test_disable_account(mock_api):
    mock_api.account_enable_account.return_value = {}
    session = WialonSession()
    session.login()
    result = disable_account(session, resource_id=1)
    assert result is None
    mock_api.account_enable_account.assert_called_once_with(
        **{"itemId": 1, "enable": 0}
    )


def test_disable_account_reraises_wialonerror(mock_api):
    mock_api.account_enable_account.side_effect = WialonError(
        6, "Unknown error"
    )
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        disable_account(session, 1)


def test_enable_account(mock_api):
    mock_api.account_enable_account.return_value = {}
    session = WialonSession()
    session.login()
    result = enable_account(session, 1)
    assert result is None
    mock_api.account_enable_account.assert_called_once_with(
        **{"itemId": 1, "enable": 1}
    )


def test_enable_account_reraises_wialonerror(mock_api):
    mock_api.account_enable_account.side_effect = WialonError(
        6, "Unknown error"
    )
    session = WialonSession()
    session.login()
    with pytest.raises(WialonError):
        enable_account(session, 1)


def test_get_command_definition_data_with_no_command_ids_returns_all(mock_api):
    mock_api.unit_get_command_definition_data.return_value = [
        {
            "id": 1,
            "n": "Ignition Off",
            "c": "custom_msg",
            "l": "vrt",
            "p": "relay#0",
            "a": 1,
            "f": 0,
            "jp": "",
        },
        {
            "id": 2,
            "n": "Ignition On",
            "c": "custom_msg",
            "l": "vrt",
            "p": "relay#1",
            "a": 1,
            "f": 0,
            "jp": "",
        },
    ]
    session = WialonSession()
    session.login()
    result = get_command_definition_data(session, unit_id=1, command_ids=None)
    assert len(result) == 2


def test_get_command_definition_data_with_command_ids(mock_api):
    mock_api.unit_get_command_definition_data.return_value = [
        {
            "id": 1,
            "n": "Ignition Off",
            "c": "custom_msg",
            "l": "vrt",
            "p": "relay#0",
            "a": 1,
            "f": 0,
            "jp": "",
        }
    ]
    session = WialonSession()
    session.login()
    result = get_command_definition_data(session, unit_id=1, command_ids=(1,))
    assert len(result) == 1


@pytest.mark.parametrize(
    "unit_id,command_name,link_type,param,timeout,flags",
    [
        (
            1,
            "Test Command #1",
            CommandLinkType.AUTO,
            "",
            300,
            CommandFlag.USE_ANY,
        ),
        (
            2,
            "Test Command #2",
            CommandLinkType.TCP,
            "",
            300,
            CommandFlag.USE_ANY,
        ),
        (
            3,
            "Test Command #3",
            CommandLinkType.UDP,
            "",
            300,
            CommandFlag.USE_ANY,
        ),
        (
            4,
            "Test Command #4",
            CommandLinkType.VRT,
            "",
            300,
            CommandFlag.USE_ANY,
        ),
        (
            5,
            "Test Command #5",
            CommandLinkType.GSM,
            "",
            300,
            CommandFlag.USE_ANY,
        ),
        (
            6,
            "Test Command #6",
            CommandLinkType.AUTO,
            "{'test': true}",
            300,
            CommandFlag.USE_ANY,
        ),
        (
            7,
            "Test Command #7",
            CommandLinkType.AUTO,
            "",
            0,
            CommandFlag.USE_ANY,
        ),
        (
            8,
            "Test Command #8",
            CommandLinkType.AUTO,
            "",
            300,
            CommandFlag.USE_PRIMARY,
        ),
        (
            9,
            "Test Command #9",
            CommandLinkType.AUTO,
            "",
            300,
            CommandFlag.USE_SECONDARY,
        ),
        (
            10,
            "Test Command #10",
            CommandLinkType.AUTO,
            "",
            300,
            CommandFlag.SEND_PARAM,
        ),
    ],
)
def test_execute_command(
    mock_api, unit_id, command_name, link_type, param, timeout, flags
):
    mock_api.unit_exec_cmd.return_value = {}
    session = WialonSession()
    session.login()
    result = execute_command(
        session,
        unit_id=unit_id,
        command_name=command_name,
        link_type=link_type,
        param=param,
        timeout=timeout,
        flags=flags,
    )
    assert not result
    mock_api.unit_exec_cmd.assert_called_once_with(
        **{
            "itemId": unit_id,
            "commandName": command_name,
            "linkType": link_type,
            "timeout": timeout,
            "flags": flags,
            "param": param,
        }
    )


@pytest.mark.parametrize("unit_id,vin", [(1, "abc"), (2, "def")])
def test_update_vin(mock_api, unit_id, vin):
    mock_api.item_update_profile_field.return_value = {}
    session = WialonSession()
    session.login()
    result = update_vin(session, unit_id, vin)
    assert not result
    mock_api.item_update_profile_field.assert_called_once_with(
        **{"itemId": unit_id, "n": "vin", "v": vin}
    )


@pytest.mark.parametrize("unit_id,new_name", [(1, "abc"), (2, "def")])
def test_update_name(mock_api, unit_id, new_name):
    mock_api.item_update_name.return_value = {}
    session = WialonSession()
    session.login()
    result = update_name(session, unit_id, new_name)
    assert not result
    mock_api.item_update_name.assert_called_once_with(
        **{"itemId": unit_id, "name": new_name}
    )


def test_get_command_name(mock_api):
    mock_api.unit_get_command_definition_data.return_value = [
        {
            "id": 1,
            "n": "Ignition Off",
            "c": "custom_msg",
            "l": "vrt",
            "p": "relay#0",
            "a": 1,
            "f": 0,
            "jp": "",
        }
    ]
    session = WialonSession()
    session.login()
    result = get_command_name(session, 1, 1)
    assert result == "Ignition Off"


def test_get_command_name_with_nonexistant_command(mock_api):
    mock_api.unit_get_command_definition_data.return_value = []
    session = WialonSession()
    session.login()
    result = get_command_name(session, 1, 1)
    assert result is None
