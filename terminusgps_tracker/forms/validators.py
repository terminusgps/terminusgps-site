import string

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.utils import get_id_from_iccid, is_unique
from terminusgps_tracker.wialonapi.items import WialonUnitGroup


def validate_django_username(value: str) -> None:
    """Raises `ValidationError` if the value represents an existing Django user name."""
    User = get_user_model()
    try:
        User.objects.get(username__iexact=value.lower())
    except User.DoesNotExist:
        return
    else:
        raise ValidationError(
            _("'%(value)s' is taken."), code="invalid", params={"value": value}
        )


def validate_wialon_imei_number(value: str) -> None:
    """Raises `ValidationError` if the value represents an invalid Wialon IMEI #."""
    with WialonSession() as session:
        unit_id: str | None = get_id_from_iccid(iccid=value.strip(), session=session)
        available = WialonUnitGroup(id="27890571", session=session)

        if unit_id is None:
            raise ValidationError(
                _("'%(value)s' was not found in the Terminus GPS database."),
                code="invalid",
                params={"value": value},
            )
        elif unit_id not in available.items:
            raise ValidationError(
                _("'%(value)s' has already been registered."),
                code="invalid",
                params={"value": value},
            )


def validate_wialon_unit_name(value: str) -> None:
    """Raises `ValidationError` if the value represents a non-unique asset name in Wialon."""
    with WialonSession() as session:
        if not is_unique(value, session, items_type="avl_unit"):
            raise ValidationError(
                _("'%(value)s' is taken."), code="invalid", params={"value": value}
            )


def validate_wialon_username(value: str) -> None:
    """Raises `ValidationError` if the value represents a non-unique user name in Wialon."""
    with WialonSession() as session:
        if not is_unique(value, session, items_type="user"):
            raise ValidationError(
                _("'%(value)s' is taken."), code="invalid", params={"value": value}
            )


def validate_wialon_resource_name(value: str) -> None:
    """Raises `ValidationError` if the value represents a non-unique user name in Wialon."""
    with WialonSession() as session:
        if not is_unique(value, session, items_type="avl_resource"):
            raise ValidationError(
                _("'%(value)s' is taken."), code="invalid", params={"value": value}
            )


def validate_wialon_password(value: str) -> None:
    """Raises `ValidationError` if the value represents an invalid Wialon password."""
    forbidden_symbols: list[str] = [",", ":", "&", "<", ">"]
    special_symbols: list[str] = [
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "*",
        "(",
        ")",
        "[",
        "]",
        "-",
        "_",
        "+",
        "-",
    ]
    if len(value) < 4:
        raise ValidationError(
            _("Password must be at least 4 chars in length. Got '%(len)s'."),
            code="invalid",
            params={"len": len(value)},
        )
    if len(value) > 32:
        raise ValidationError(
            _("Password cannot be longer than 32 chars. Got '%(len)s'."),
            code="invalid",
            params={"len": len(value)},
        )
    if value.startswith(" ") or value.endswith(" "):
        raise ValidationError(
            _("Password cannot start or end with a space."), code="invalid"
        )
    if any([char for char in value if char in forbidden_symbols]):
        raise ValidationError(
            _(
                "Password cannot contain a forbidden symbol. Forbidden symbols: '%(symbols)s'."
            ),
            code="invalid",
            params={"symbols": forbidden_symbols},
        )
    if not any([char for char in value if char in special_symbols]):
        raise ValidationError(
            _(
                "Password must contain at least one special symbol. Special symbols: '%(symbols)s'"
            ),
            code="invalid",
            params={"symbols": special_symbols},
        )
    if not any([char for char in value if char in string.ascii_lowercase]):
        raise ValidationError(
            _("Password must contain at least one lowercase letter."), code="invalid"
        )
    if not any([char for char in value if char in string.ascii_uppercase]):
        raise ValidationError(
            _("Password must contain at least one uppercase letter."), code="invalid"
        )
    if not any([char for char in value if char in string.digits]):
        raise ValidationError(
            _("Password must contain at least one digit."), code="invalid"
        )
