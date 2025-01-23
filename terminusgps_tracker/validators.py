import string

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from wialon.api import WialonError

from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.items import WialonUnitGroup, WialonUnit
from terminusgps.wialon.utils import get_id_from_iccid, is_unique


def validate_phone(value: str) -> None:
    """Raises `ValidationError` if the value does not represent a valid phone number."""
    if not value.startswith("+"):
        raise ValidationError(
            _("Phone number must begin with a '+', got: '(value)%s'"),
            code="invalid",
            params={"value": value},
        )
    if " " in value:
        raise ValidationError(_("Phone number cannot contain spaces."), code="invalid")
    return


def validate_wialon_asset_id(value: str) -> None:
    if not hasattr(settings, "WIALON_TOKEN"):
        raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")

    with WialonSession() as session:
        try:
            # Construct a unit with the id
            WialonUnit(id=value, session=session)
        except WialonError or ValueError:
            raise ValidationError(
                _("'%(value)s' was not found in the Wialon database."),
                code="invalid",
                params={"value": value},
            )


def validate_wialon_imei_number(value: str) -> None:
    """Raises `ValidationError` if the value represents an invalid Wialon IMEI #."""
    if not hasattr(settings, "WIALON_TOKEN"):
        raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")
    if not hasattr(settings, "WIALON_UNACTIVATED_GROUP"):
        raise ImproperlyConfigured("'WIALON_UNACTIVATED_GROUP' setting is required.")

    with WialonSession() as session:
        unit_id: str | None = get_id_from_iccid(iccid=value.strip(), session=session)
        available = WialonUnitGroup(
            id=str(settings.WIALON_UNACTIVATED_GROUP), session=session
        )

        if unit_id is None:
            raise ValidationError(
                _("'%(value)s' was not found in the Terminus GPS database."),
                code="invalid",
                params={"value": value},
            )
        elif str(unit_id) not in available.items:
            raise ValidationError(
                _("'%(value)s' has already been registered."),
                code="invalid",
                params={"value": value},
            )
    return


def validate_wialon_unit_name(value: str) -> None:
    """Raises `ValidationError` if the value represents a non-unique asset name in Wialon."""
    if not hasattr(settings, "WIALON_TOKEN"):
        raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")

    with WialonSession(token=settings.WIALON_TOKEN) as session:
        if not is_unique(value, session, items_type="avl_unit"):
            raise ValidationError(
                _("'%(value)s' is taken."), code="invalid", params={"value": value}
            )
    return


def validate_wialon_username(value: str) -> None:
    """Raises `ValidationError` if the value represents a non-unique user name in Wialon."""
    if not hasattr(settings, "WIALON_TOKEN"):
        raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")

    with WialonSession() as session:
        if not is_unique(value, session, items_type="user"):
            raise ValidationError(
                _("'%(value)s' is taken."), code="invalid", params={"value": value}
            )
    return


def validate_wialon_resource_name(value: str) -> None:
    """Raises `ValidationError` if the value represents a non-unique user name in Wialon."""
    if not hasattr(settings, "WIALON_TOKEN"):
        raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")

    with WialonSession() as session:
        if not is_unique(value, session, items_type="avl_resource"):
            raise ValidationError(
                _("'%(value)s' is taken."), code="invalid", params={"value": value}
            )
    return


def validate_wialon_password(value: str) -> None:
    """Raises `ValidationError` if the value represents an invalid Wialon password."""
    forbidden_symbols: list[str] = [",", ":", "&", "<", ">", "'"]
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
    ]
    if value.startswith(" ") or value.endswith(" "):
        raise ValidationError(_("Cannot start or end with a space."), code="invalid")
    if len(value) < 4:
        raise ValidationError(
            _("Must be at least 4 chars in length. Got '%(len)s'."),
            code="invalid",
            params={"len": len(value)},
        )
    elif len(value) > 32:
        raise ValidationError(
            _("Cannot be longer than 32 chars. Got '%(len)s'."),
            code="invalid",
            params={"len": len(value)},
        )
    if not any([char for char in value if char in string.ascii_uppercase]):
        raise ValidationError(
            _("Must contain at least one uppercase letter."), code="invalid"
        )
    if not any([char for char in value if char in string.ascii_lowercase]):
        raise ValidationError(
            _("Must contain at least one lowercase letter."), code="invalid"
        )
    if not any([char for char in value if char in special_symbols]):
        raise ValidationError(
            _("Must contain at least one special symbol."), code="invalid"
        )
    for char in value:
        if char in forbidden_symbols:
            raise ValidationError(
                _("Cannot contain forbidden '%(char)s' character."),
                code="invalid",
                params={"char": char},
            )
    return
