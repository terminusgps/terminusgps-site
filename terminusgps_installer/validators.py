from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_vin(value: str) -> None:
    return


def validate_imei(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(
            _("IMEI # cannot contain non-digits, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
