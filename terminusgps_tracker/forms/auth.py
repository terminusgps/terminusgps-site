from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import validate_email
from django.forms import widgets

from terminusgps_tracker.validators import (
    validate_wialon_password,
    validate_wialon_username,
)


class TrackerSignupForm(UserCreationForm):
    field_order = ["first_name", "last_name", "username", "password1", "password2"]
    default_css_class = (
        "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white"
    )

    first_name = forms.CharField(
        label="First Name",
        max_length=64,
        widget=widgets.TextInput(
            attrs={"class": default_css_class, "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=64,
        widget=widgets.TextInput(
            attrs={"class": default_css_class, "placeholder": "Last Name"}
        ),
    )
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email, validate_wialon_username],
        widget=widgets.EmailInput(
            attrs={"class": default_css_class, "placeholder": "Email Address"}
        ),
    )
    password1 = forms.CharField(
        widget=widgets.PasswordInput(
            attrs={"class": default_css_class, "placeholder": "Password"}
        ),
        validators=[validate_wialon_password],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=widgets.PasswordInput(
            attrs={"class": default_css_class, "placeholder": "Confirm Password"}
        ),
        validators=[validate_wialon_password],
    )


class TrackerAuthenticationForm(AuthenticationForm):
    default_css_class = (
        "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white"
    )
    error_messages = {
        "invalid_login": "Couldn't find a user with those credentials. Please try again."
    }
    username = forms.CharField(
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=widgets.EmailInput(
            attrs={
                "class": default_css_class,
                "placeholder": "dylan@terminusgps.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        min_length=8,
        max_length=32,
        widget=widgets.PasswordInput(
            attrs={"class": default_css_class, "placeholder": "••••••••••••••••"}
        ),
    )
