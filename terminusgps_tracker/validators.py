from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
        [
            digit * 2 if digit * 2 <= 9 else (digit * 2) % 9 or 9
            for digit in even_digits
        ]
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
            _(
                "Month must be exactly 2 characters in length, got '%(length)s'"
            ),
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
