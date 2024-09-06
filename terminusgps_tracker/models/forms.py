from typing import Any
from django import forms
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.validators import (
    validate_contains_digit,
    validate_contains_lowercase_letter,
    validate_contains_special_symbol,
    validate_contains_uppercase_letter,
    validate_imei_number_is_available,
)

class RegistrationForm(forms.Form):
    imei_number = forms.CharField(
        label="IMEI #",
        min_length=4,
        max_length=17,
        required=True,
        help_text="You can find this underneath the QR Code you received with your vehicle.",
        validators=[validate_imei_number_is_available],
    )
    asset_name = forms.CharField(
        label="Asset Name",
        min_length=4,
        max_length=128,
        required=True,
        help_text="This is what your vehicle will be named in the Terminus GPS app."
    )
    email = forms.EmailField(
        label="Email Address",
        min_length=4,
        max_length=128,
        required=True,
        help_text="A good email address we can reach you at."
    )
    wialon_password_1 = forms.CharField(
        label="Password",
        min_length=8,
        max_length=32,
        required=True,
        validators=[
            validate_contains_digit,
            validate_contains_lowercase_letter,
            validate_contains_special_symbol,
            validate_contains_uppercase_letter,
        ],
        widget=forms.PasswordInput(),
    )
    wialon_password_2 = forms.CharField(
        label="Confirm Password",
        min_length=8,
        max_length=32,
        required=True,
        validators=[
            validate_contains_digit,
            validate_contains_lowercase_letter,
            validate_contains_special_symbol,
            validate_contains_uppercase_letter,
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
