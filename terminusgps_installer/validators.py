from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_vin(value: str) -> None:
    wmi = value[:3]
    vds = value[3:8]
    check = value[8]
    year = value[9]
    plant = value[10]
    sequence = value[11:]
    return


def validate_imei(value: str) -> None:
    return


def validate_is_digit(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(
            _("This value cannot contain non-digits, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
