import string

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.items.unit_group import WialonUnitGroup


def validate_imei_number_exists(value: str) -> None:
    """Raises `ValidationError` if the value does not represent a unit in the Terminus GPS database."""
    with WialonSession() as session:
        unit_id: str | None = session.get_id_from_iccid(iccid=value.strip())
        if not unit_id:
            raise ValidationError(
                _(
                    "'%(value)s' was not found in the Terminus GPS database. Please ensure your IMEI # is correctly input."
                ),
                params={"value": value.strip()},
                code="invalid",
            )


def validate_asset_name_is_unique(value: str) -> None:
    """Raises `ValidationError` if the value represents a non-unique asset name in Wialon."""
    with WialonSession() as session:
        result = session.wialon_api.core_check_unique(
            **{"type": "avl_unit", "value": value}
        ).get("result", 1)
        if result:
            raise ValidationError(
                _("'%(value)s' is taken. Please try another value."),
                params={"value": value},
                code="invalid",
            )


def validate_starts_with_plus_one(value: str) -> None:
    """Raises `ValidationError` if the value does not start with '+1'."""
    if not value.startswith("+1"):
        raise ValidationError(
            _("Ensure '%(value)s' begins with a '+1'."),
            params={"value": value},
            code="invalid",
        )


def validate_django_username_is_unique(value: str) -> None:
    user_model = get_user_model()
    try:
        user_model.objects.get(username=value)
    except user_model.DoesNotExist:
        return
    else:
        raise ValidationError(
            _("'%(value)s' is taken."), params={"value": value}, code="invalid"
        )


def validate_does_not_contain_hyphen(value: str) -> None:
    """Raises `ValidationError` if the value contains a hyphen."""
    if "-" in value:
        raise ValidationError(
            _("Ensure '%(value)s' does not contain a hyphen: '-'."),
            params={"value": value},
            code="invalid",
        )


def validate_does_not_contain_forbidden_symbol(value: str) -> None:
    """Raises `ValidationError` if the value contains a forbidden symbol."""
    forbidden_symbols: str = '"<>{},\\'
    if any(char in list(forbidden_symbols) for char in value):
        raise ValidationError(
            _(
                "Ensure this value does not contain a forbidden symbol. Forbidden symbols: '%(symbols)s'"
            ),
            params={
                "symbols": [
                    "less than (<)",
                    "greater than (>)",
                    "open curly ({)",
                    "close curly (})",
                    "comma (,)",
                    "backslash (\\)",
                ]
            },
            code="invalid",
        )


def validate_imei_number_is_available(value: str) -> None:
    """Raises `ValidationError` if the value represents an invalid/unavailable unit in the Terminus GPS database."""
    with WialonSession() as session:
        unit_id: str | None = session.get_id_from_iccid(iccid=value.strip())
        available = WialonUnitGroup(id="27890571", session=session)
        if not unit_id:
            raise ValidationError(
                _(
                    "'%(value)s' was not found in the Terminus GPS database. Please ensure your IMEI # is correctly input."
                ),
                params={"value": value.strip()},
                code="invalid",
            )

        if unit_id not in available.items:
            raise ValidationError(
                _("'%(value)s' is unavailable at this time. Please try again later."),
                params={"value": value.strip()},
                code="invalid",
            )


def validate_wialon_username_is_unique(value: str) -> None:
    """Raises `ValidationError` if the value would create a non-unique user in the Terminus GPS Wialon database."""
    with WialonSession() as session:
        result = session.wialon_api.core_check_unique(
            **{"type": "user", "value": value.strip()}
        ).get("result", 1)
        if result:
            raise ValidationError(
                _("'%(value)s' is taken. Please try another value."),
                params={"value": value},
                code="invalid",
            )


def validate_contains_uppercase_letter(value: str) -> None:
    """Raises `ValidationError` if value does not contain an uppercase letter."""
    if not any(char in string.ascii_uppercase for char in value):
        raise ValidationError(
            _("Ensure this value contains at least one uppercase letter."),
            code="invalid",
        )


def validate_contains_lowercase_letter(value: str) -> None:
    """Raises `ValidationError` if value does not contain a lowercase letter."""
    if not any(char in string.ascii_lowercase for char in value):
        raise ValidationError(
            _("Ensure this value contains at least one lowercase letter."),
            code="invalid",
        )


def validate_contains_digit(value: str) -> None:
    """Raises `ValidationError` if value does not contain a digit."""
    if not any(char in string.digits for char in value):
        raise ValidationError(
            _("Ensure this value contains at least one digit."), code="invalid"
        )


def validate_contains_special_symbol(value: str) -> None:
    """Raises `ValidationError` if value does not contain a special symbol."""
    special_symbols: str = "'/;?@!#$^-_=+|"
    if not any(char in list(special_symbols) for char in value):
        raise ValidationError(
            _(
                "Ensure this value contains at least one of these symbols: '%(symbols)s'"
            ),
            params={"symbols": list(special_symbols)},
            code="invalid",
        )
