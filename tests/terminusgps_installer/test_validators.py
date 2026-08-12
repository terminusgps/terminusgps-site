import pytest
from django.core.exceptions import ValidationError
from wialon.api import WialonError

from terminusgps_installer.validators import (
    validate_imei,
    validate_is_digit,
    validate_vin,
)


def test_validate_imei_good_input(mock_api):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1, "nm": "Unit #1"}],
    }
    assert validate_imei("abc123") is None


def test_validate_imei_bad_input(mock_api):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 2,
        "items": [{"id": 1, "nm": "Unit #1"}, {"id": 2, "nm": "Unit #2"}],
    }
    with pytest.raises(ValidationError):
        validate_imei("abc123")


def test_validate_imei_wialon_api_error(mock_api):
    mock_api.core_search_items.side_effect = WialonError(1, "Invalid session")
    with pytest.raises(ValidationError):
        validate_imei("abc123")


def test_validate_vin_good_input():
    assert validate_vin("abc123") is None


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "55",
        "9001",
        "1930809203848093804280324",
        "applesauce",
        "123234l23456",
        "9900O09234",
    ],
)
def test_validate_is_digit(value):
    if value.isdigit():
        assert validate_is_digit(value) is None
    else:
        with pytest.raises(ValidationError):
            validate_is_digit(value)
