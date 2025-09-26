from string import ascii_lowercase, ascii_uppercase, digits, punctuation

from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_wialon_password(value: str) -> None:
    """Raises :py:exec:`~django.core.exceptions.ValidationError` if the value is an invalid Wialon password."""
    if len(value) < 8:
        raise ValidationError(
            _(
                "Password must be greater than 8 characters in length, got %(len)s."
            ),
            code="invalid",
            params={"len": len(value)},
        )
    if len(value) > 64:
        raise ValidationError(
            _(
                "Password must be less than 64 characters in length, got %(len)s."
            ),
            code="invalid",
            params={"len": len(value)},
        )
    uppercase_chars = [char for char in value if char in ascii_uppercase]
    lowercase_chars = [char for char in value if char in ascii_lowercase]
    punctuation_chars = [char for char in value if char in punctuation]
    digit_chars = [char for char in value if char in digits]
    if len(uppercase_chars) < 1:
        raise ValidationError(
            _("Password must contain at least one uppercase letter."),
            code="invalid",
        )
    if len(lowercase_chars) < 1:
        raise ValidationError(
            _("Password must contain at least one lowercase letter."),
            code="invalid",
        )
    if len(punctuation_chars) < 1:
        raise ValidationError(
            _("Password must contain at least one special symbol."),
            code="invalid",
        )
    if len(digit_chars) < 1:
        raise ValidationError(
            _("Password must contain at least one digit."), code="invalid"
        )


class TerminusgpsRegisterForm(UserCreationForm):
    def clean_username(self):
        super().clean_username()
        if username := self.cleaned_data.get("username"):
            try:
                validate_email(username)
                return username
            except ValidationError as e:
                self.add_error("username", e)

    def clean_password1(self):
        super().clean_password1()
        if password := self.cleaned_data.get("password1"):
            try:
                validate_wialon_password(password)
            except ValidationError as e:
                self.add_error("password1", e)
