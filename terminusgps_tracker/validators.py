import string

from authorizenet import apicontractsv1, apicontrollers
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from terminusgps.authorizenet.auth import get_merchant_auth
from terminusgps.wialon.items import WialonUnitGroup
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_imei, is_unique


class WialonValidatorBase:
    def __init__(self) -> None:
        self.session: WialonSession = WialonSession()
        self.session.login(self.session.token)

    def __call__(self, value: str) -> None:
        raise NotImplementedError("Subclasses must implement this method.")


class WialonNameUniqueValidator(WialonValidatorBase):
    def __init__(self, items_type: str, **kwargs) -> None:
        self.items_type = items_type
        return super().__init__(**kwargs)

    def __call__(self, value: str) -> None:
        if not is_unique(value, self.session, items_type=self.items_type):
            raise ValidationError(
                _("'%(value)s' is taken."), code="invalid", params={"value": value}
            )


class WialonUnitAvailableValidator(WialonValidatorBase):
    def __init__(self, *args, **kwargs) -> None:
        if not hasattr(settings, "WIALON_UNACTIVATED_GROUP"):
            raise ImproperlyConfigured(
                "'WIALON_UNACTIVATED_GROUP' setting is required."
            )

        super().__init__(*args, **kwargs)

    def __call__(self, value: str) -> None:
        if not value.isdigit():
            raise ValidationError(
                _("'%(value)s' cannot contain non-digits."),
                code="invalid",
                params={"value": value},
            )
        unit_id: str | None = get_id_from_imei(value, session=self.session)
        if not unit_id:
            raise ValidationError(
                _("'%(value)s' wasn't found in Wialon."),
                code="invalid",
                params={"value": value},
            )
        available: WialonUnitGroup = WialonUnitGroup(
            id=settings.WIALON_UNACTIVATED_GROUP, session=self.session
        )
        if unit_id not in available.items:
            raise ValidationError(
                _("Whoops! '%(value)s' has already been registered."),
                code="invalid",
                params={"value": value},
            )


def validate_customer_profile_id(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(
            _("Customer profile id must be a digit. Got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )

    request = apicontractsv1.getCustomerProfileRequest(
        merchantAuthenticator=get_merchant_auth(),
        customerProfileId=value,
        includeIssuerInfo="false",
    )
    controller = apicontrollers.getCustomerProfileController(request)
    controller.execute()
    response = controller.getresponse()

    if not response or response.messages.resultCode != "Ok":
        raise ValidationError(
            _("Failed to retrieve customer profile #%(id)s"),
            code="invalid",
            params={"id": value},
        )


def validate_credit_card_number(value: str) -> None:
    if not value.isdigit():
        raise ValidationError(
            _("Card number must be a digit. Got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )

    card_number = [int(num) for num in reversed(value)]
    even_digits = card_number[1::2]
    odd_digits = card_number[0::2]

    checksum = 0
    checksum += sum(
        [digit * 2 if digit * 2 <= 9 else (digit * 2) % 9 or 9 for digit in even_digits]
    )
    checksum += sum([digit for digit in odd_digits])

    if checksum % 10 != 0:
        raise ValidationError(_("Invalid credit card number."), code="invalid")


def validate_credit_card_expiry_month(value: str) -> None:
    months = [str(num + 1) for num in range(12)]
    if not value.isdigit():
        raise ValidationError(
            _("Month must be a digit, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
    if not len(value) == 2:
        raise ValidationError(
            _("Month must be exactly 2 characters in length, got '%(length)s'"),
            code="invalid",
            params={"length": len(value)},
        )
    if value not in months:
        raise ValidationError(
            _("Month must be 1-12, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )


def validate_credit_card_expiry_year(value: str) -> None:
    this_year = int(f"{timezone.now():%y}")
    if not value.isdigit():
        raise ValidationError(
            _("Year must be a digit, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )
    if not len(value) == 2:
        raise ValidationError(
            _("Year must be exactly 2 characters in length, got '%(length)s'"),
            code="invalid",
            params={"length": len(value)},
        )
    if int(value) < this_year:
        raise ValidationError(
            _("Year is in the past, got '%(value)s'."),
            code="invalid",
            params={"value": value},
        )


def validate_wialon_imei_number_available(value: str) -> None:
    return WialonUnitAvailableValidator()(value)


def validate_wialon_unit_name_unique(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value is a non-unique Wialon asset name."""
    return WialonNameUniqueValidator(items_type="avl_unit")(value)


def validate_wialon_user_name_unique(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value is a non-unique Wialon user name."""
    return WialonNameUniqueValidator(items_type="user")(value)


def validate_wialon_resource_name_unique(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value is a non-unique Wialon resource name."""
    return WialonNameUniqueValidator(items_type="avl_resource")(value)


def validate_wialon_unit_group_name_unique(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value is a non-unique Wialon unit group name."""
    return WialonNameUniqueValidator(items_type="avl_unit_group")(value)


def validate_wialon_password(value: str) -> None:
    """Raises :py:exec:`ValidationError` if the value represents an invalid Wialon password."""
    special_symbols_0: list[str] = ["!", "@", "#", "$", "%", "^", "*"]
    special_symbols_1: list[str] = ["(", ")", "[", "]", "-", "_", "+"]
    forbidden_symbols: list[str] = [",", ":", "&", "<", ">", "'"]
    value = value.strip() if value.startswith(" ") or value.endswith(" ") else value

    if len(value) < 4:
        raise ValidationError(
            _("Password cannot be less than 4 characters in length. Got '%(len)s'."),
            code="invalid",
            params={"len": len(value)},
        )
    if len(value) > 64:
        raise ValidationError(
            _(
                "Password cannot be greater than 64 characters in length. Got '%(len)s'."
            ),
            code="invalid",
            params={"len": len(value)},
        )
    if not any([char for char in value if char in string.ascii_uppercase]):
        raise ValidationError(
            _("Password must contain at least one uppercase letter."), code="invalid"
        )
    if not any([char for char in value if char in string.ascii_lowercase]):
        raise ValidationError(
            _("Password must contain at least one lowercase letter."), code="invalid"
        )
    if not any(
        [char for char in value if char in special_symbols_0 + special_symbols_1]
    ):
        raise ValidationError(
            _("Password must contain at least one special symbol."), code="invalid"
        )
    for char in value:
        if char in forbidden_symbols:
            raise ValidationError(
                _("Password cannot contain forbidden character '%(char)s'."),
                code="invalid",
                params={"char": char},
            )
