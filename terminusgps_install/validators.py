from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_vin_number(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value is an invalid VIN number."""
    if not len(value) == 17:
        raise ValidationError(
            _("Whoops! VIN # must be exactly 17 characters long, got %(len)s."),
            code="invalid",
            params={"len": len(value)},
        )
