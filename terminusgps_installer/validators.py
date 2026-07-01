import wialon.api
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps.wialon import get_session, get_unit_by_imei


def validate_vin(value: str) -> None:
    wmi = value[:3]
    vds = value[3:8]
    check = value[8]
    year = value[9]
    plant = value[10]
    sequence = value[11:]
    return


def validate_imei(value: str) -> None:
    session = get_session(sid=None)
    try:
        get_unit_by_imei(session, value)
    except wialon.api.WialonError as error:
        if error._code == -1:
            raise ValidationError(
                _("Failed to find a unit with this IMEI. It may not exist."),
                code="invalid",
                params={"value": value},
            )
        else:
            raise ValidationError(
                _("%(error)s"), code="invalid", params={"error": error}
            )


def validate_is_digit(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(
            _("This value cannot contain non-digits, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
