import pytest
from django.core.exceptions import ValidationError

from terminusgps_installer.validators import validate_is_digit


@pytest.mark.parametrize(
    "value", ["1", "55", "9001", "1930809203848093804280324"]
)
def test_validate_imei(value):
    return


@pytest.mark.parametrize(
    "value", ["1", "55", "9001", "1930809203848093804280324"]
)
def test_validate_is_digit_good_input(value):
    assert validate_is_digit(value) is None


@pytest.mark.parametrize("value", ["applesauce", "123234l23456", "9900O09234"])
def test_validate_is_digit_bad_input(value):
    with pytest.raises(ValidationError):
        validate_is_digit(value)
