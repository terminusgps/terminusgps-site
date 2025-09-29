from string import ascii_lowercase, ascii_uppercase, digits, punctuation

from django import forms
from django.contrib.auth.forms import BaseUserCreationForm
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


class TerminusgpsRegisterForm(BaseUserCreationForm):
    first_name = forms.CharField(
        max_length=64, help_text="Please enter your first name."
    )
    last_name = forms.CharField(
        max_length=64, help_text="Please enter your last name."
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].validators.append(validate_email)
        self.fields["password1"].validators.append(validate_wialon_password)
        self.fields["password2"].validators.append(validate_wialon_password)

        self.fields[
            "username"
        ].help_text = "Required. Please enter a valid email address."
