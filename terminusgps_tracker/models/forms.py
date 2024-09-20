from typing import Any
from django import forms
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.validators import (
    validate_contains_digit,
    validate_contains_lowercase_letter,
    validate_contains_special_symbol,
    validate_contains_uppercase_letter,
    validate_does_not_contain_forbidden_symbol,
    validate_imei_number_is_available,
    validate_starts_with_plus_one,
    validate_username_is_unique,
    validate_does_not_contain_hyphen,
)

class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        min_length=1,
        max_length=128,
        required=True,
        help_text="Your first name.",
        validators=[validate_does_not_contain_forbidden_symbol],
    )
    last_name = forms.CharField(
        label="Last Name",
        min_length=1,
        max_length=128,
        required=True,
        help_text="Your last name.",
        validators=[validate_does_not_contain_forbidden_symbol],
    )
    email = forms.EmailField(
        label="Email Address",
        min_length=4,
        max_length=128,
        required=True,
        help_text="A good email address.",
        validators=[
            validate_does_not_contain_forbidden_symbol,
            validate_username_is_unique,
        ],
    )
    phone_number = forms.CharField(
        label="Phone #",
        max_length=14,
        required=False,
        help_text="This phone will receive notifications concerning your Terminus GPS assets.",
        validators=[
            validate_does_not_contain_hyphen,
            validate_starts_with_plus_one,
        ],
    )
    imei_number = forms.CharField(
        label="IMEI #",
        min_length=4,
        max_length=17,
        required=True,
        help_text="You can find this number underneath the QR Code you received with your vehicle.",
        validators=[validate_imei_number_is_available],
    )
    wialon_password_1 = forms.CharField(
        label="Password",
        min_length=8,
        max_length=32,
        required=True,
        help_text="The password for your new Terminus GPS account.",
        validators=[
            validate_contains_digit,
            validate_contains_lowercase_letter,
            validate_contains_special_symbol,
            validate_contains_uppercase_letter,
            validate_does_not_contain_forbidden_symbol,
        ],
        widget=forms.PasswordInput(),
    )
    wialon_password_2 = forms.CharField(
        label="Confirm Password",
        min_length=8,
        max_length=32,
        required=True,
        help_text="Repeat the password for your new Terminus GPS account.",
        validators=[
            validate_contains_digit,
            validate_contains_lowercase_letter,
            validate_contains_special_symbol,
            validate_contains_uppercase_letter,
            validate_does_not_contain_forbidden_symbol,
        ],
        widget=forms.PasswordInput(),
    )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean()
        if cleaned_data is not None:
            password_1 = cleaned_data.get("wialon_password_1")
            password_2 = cleaned_data.get("wialon_password_2")

            if password_1 and password_2:
                if password_1 != password_2:
                    self.add_error("wialon_password_1", ValidationError(_("Passwords do not match.")))
                    self.add_error("wialon_password_2", ValidationError(_("Passwords do not match.")))

        return cleaned_data
