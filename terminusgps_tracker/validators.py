import string

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.wialonapi.session import WialonSession

def validate_imei_number_is_available(value: str) -> None:
    """Raises `django.ValidationError` unless value is a valid IMEI #."""
    with WialonSession() as session:
        params = {
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": f"*{value}*",
                "sortType": "sys_unique_id",
                "propType": "property",
                "or_logic": 0,
            },
            "force": 0,
            "flags": 1,
            "from": 0,
            "to": 0,
        }
        response = session.wialon_api.core_search_items(**params)

    items = response.get("items", [])
    if len(items) != 1:
        raise ValidationError(_("IMEI # '%(value)s' could not be located in the Terminus GPS database."), params={"value": value})
    elif items[0].get("nm") != value:
        raise ValidationError(_("IMEI # '%(value)s' is unavailable."), params={"value": value}, code="invalid")
    return


def validate_contains_uppercase_letter(value: str) -> None:
    """Returns input value if it contains an uppercase letter, otherwise raises `django.core.exceptions.ValidationError`."""
    if not any(char in string.ascii_uppercase for char in value):
        raise ValidationError(_("Ensure this value contains at least one uppercase letter."), code="invalid")
    return

def validate_contains_lowercase_letter(value: str) -> None:
    """Returns input value if it contains a lowercase letter, otherwise raises `django.core.exceptions.ValidationError`."""
    if not any(char in string.ascii_lowercase for char in value):
        raise ValidationError(_("Ensure this value contains at least one lowercase letter."), code="invalid")
    return

def validate_contains_digit(value: str) -> None:
    """Returns input value if it contains a digit, otherwise raises `django.core.exceptions.ValidationError`."""
    if not any(char in string.digits for char in value):
        raise ValidationError(_("Ensure this value contains at least one digit."), code="invalid")
    return

def validate_contains_special_symbol(value: str) -> None:
    """Returns input value if it contains a special symbol, otherwise raises `django.core.exceptions.ValidationError`."""
    special_symbols: str = "@#$%!?&_-"
    if not any(char in list(special_symbols) for char in value):
        raise ValidationError(
            _("Ensure this value contains at least one of these symbols: '%(symbols)s'"),
            params={"symbols": list(special_symbols)},
            code="invalid"
        )
    return
