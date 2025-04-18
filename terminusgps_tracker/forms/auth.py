from typing import Any

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import validate_email
from django.forms import ValidationError, widgets
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.validators import validate_wialon_password


class TrackerEmailVerificationForm(forms.Form):
    otp = forms.CharField(
        label="One-time Password (OTP)",
        max_length=6,
        widget=widgets.TextInput(
            attrs={
                "class": "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"
            }
        ),
    )


class TrackerRegisterForm(UserCreationForm):
    field_order = ["first_name", "last_name", "username", "password1", "password2"]
    default_css_class = "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"

    first_name = forms.CharField(
        label="First Name",
        max_length=64,
        widget=widgets.TextInput(
            attrs={"class": default_css_class, "placeholder": "First"}
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=64,
        widget=widgets.TextInput(
            attrs={"class": default_css_class, "placeholder": "Last"}
        ),
    )
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=widgets.EmailInput(
            attrs={
                "class": default_css_class,
                "placeholder": "email@terminusgps.com",
                "inputmode": "email",
            }
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=widgets.PasswordInput(
            attrs={
                "class": default_css_class,
                "minlength": 4,
                "maxlength": 64,
                "inputmode": "text",
            }
        ),
        validators=[validate_wialon_password],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=widgets.PasswordInput(
            attrs={
                "class": default_css_class,
                "minlength": 4,
                "maxlength": 64,
                "inputmode": "text",
            }
        ),
        validators=[validate_wialon_password],
    )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean()
        if isinstance(cleaned_data, dict):
            password1 = cleaned_data.get("password1")
            password2 = cleaned_data.get("password2")

            if password1 and password2 and password1 != password2:
                raise ValidationError(_("Passwords do not match."), code="invalid")

        return cleaned_data


class TrackerAuthenticationForm(AuthenticationForm):
    default_css_class = "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"
    error_messages = {
        "invalid_login": "Couldn't find a user with those credentials. Please try again."
    }
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=widgets.EmailInput(
            attrs={
                "class": default_css_class,
                "placeholder": "email@terminusgps.com",
                "autofocus": True,
                "inputmode": "email",
            }
        ),
    )
    password = forms.CharField(
        min_length=8,
        max_length=64,
        widget=widgets.PasswordInput(attrs={"class": default_css_class}),
    )
