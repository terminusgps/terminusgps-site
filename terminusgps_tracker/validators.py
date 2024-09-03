import string

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_contains_uppercase_letter(value: str) -> str:
    """Raises `django.ValidationError` unless value contains at least one uppercase letter."""
    if not any(char in string.ascii_uppercase for char in value):
        raise ValidationError(_("Value must contain at least one uppercase letter."))
    return value

def validate_contains_lowercase_letter(value: str) -> str:
    """Raises `django.ValidationError` unless value contains at least one lowercase letter."""
    if not any(char in string.ascii_lowercase for char in value):
        raise ValidationError(_("Value must contain at least one lowercase letter."))
    return value

def validate_contains_digit(value: str) -> str:
    """Raises `django.ValidationError` unless value contains at least one digit."""
    if not any(char in string.digits for char in value):
        raise ValidationError(_("Value must contain at least one lowercase letter."))
    return value

def validate_contains_special_symbol(value: str) -> str:
    """Raises `django.ValidationError` unless value contains at least one special symbol."""
    special_symbols: set[str] = set("@#$%!?&_-")
    if not any(char in special_symbols for char in value):
        raise ValidationError(
            _("Value must contain at least one special symbol. Symbols: '%(symbols)s'"),
            params={"symbols": special_symbols}
        )
    return value

def validate_wialon_compliant_password(value: str) -> str:
    """Raises `django.ValidationError` unless value is a Wialon compliant password."""
    validate_contains_uppercase_letter(value)
    validate_contains_lowercase_letter(value)
    validate_contains_digit(value)
    validate_contains_special_symbol(value)
    return value
