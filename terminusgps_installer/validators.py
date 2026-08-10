from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wialon.api import WialonError

from terminusgps.wialon import get_session, get_unit_by_imei


def validate_vin(value: str) -> None:
    return


def validate_imei(value: str) -> None:
    session = get_session(sid=None)
    try:
        get_unit_by_imei(session, value)
    except WialonError as error:
        if error._code == -1:
            raise ValidationError("Invalid IMEI #.", code="invalid")
        else:
            raise ValidationError(
                "%(error)s", code="invalid", params={"error": error}
            )


def validate_is_digit(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(
            _("This value cannot contain non-digits, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
