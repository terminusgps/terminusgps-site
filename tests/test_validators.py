import pytest
from django.core.exceptions import ValidationError

from terminusgps_installer.validators import (
    validate_imei,
    validate_is_digit,
    validate_vin,
)


@pytest.mark.parametrize(
    "value", ["1", "55", "9001", "1930809203848093804280324"]
)
def test_validate_imei_good_input(mock_api, value):
    mock_api.core_search_items.return_value = {
        "totalItemsCount": 1,
        "items": [{"id": 1, "nm": "Unit #1"}],
    }
    assert validate_imei(value) is None


@pytest.mark.parametrize(
    "value", ["1", "55", "9001", "1930809203848093804280324"]
)
def test_validate_vin_good_input(value):
    assert validate_vin(value) is None


@pytest.mark.parametrize(
    "value", ["1", "55", "9001", "1930809203848093804280324"]
)
def test_validate_is_digit_good_input(value):
    assert validate_is_digit(value) is None


@pytest.mark.parametrize("value", ["applesauce", "123234l23456", "9900O09234"])
def test_validate_is_digit_bad_input(value):
    with pytest.raises(ValidationError):
        validate_is_digit(value)
