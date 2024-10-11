from typing import Any

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.validators import (
    validate_django_username_is_unique,
    validate_imei_number_is_available,
    validate_wialon_username_is_unique,
)
from terminusgps_tracker.forms.widgets import (
    CustomEmailInput,
    CustomTextInput,
    CustomPasswordInput,
)


class CustomerAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email Address", validators=[validate_email])
    password = forms.CharField(label="Password")


class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name", min_length=1, max_length=64, widget=CustomTextInput
    )
    last_name = forms.CharField(
        label="Last Name", min_length=1, max_length=64, widget=CustomTextInput
    )
    email = forms.EmailField(
        label="Email Address",
        validators=[
            validate_wialon_username_is_unique,
            validate_django_username_is_unique,
        ],
        widget=CustomEmailInput,
    )
    password1 = forms.CharField(label="Password", widget=CustomPasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=CustomPasswordInput)

    def clean(self) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean()
        if cleaned_data is not None:
            password1, password2 = (
                cleaned_data.get("password1"),
                cleaned_data.get("password2"),
            )

            if password1 != password2:
                self.add_error(
                    "password1",
                    ValidationError(_("Passwords do not match."), code="invalid"),
                )
                self.add_error(
                    "password2",
                    ValidationError(_("Passwords do not match."), code="invalid"),
                )
        return cleaned_data
