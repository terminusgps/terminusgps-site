from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import validate_email
from django.forms import widgets

from terminusgps_tracker.validators import (
    validate_wialon_password,
    validate_wialon_username,
)


class TrackerRegistrationForm(UserCreationForm):
    field_order = ["first_name", "last_name", "username", "password1", "password2"]
    default_css_class = "w-full block mt-2 mb-4 p-2 rounded-md text-black dark:bg-gray-800 dark:text-white"

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
        validators=[validate_email, validate_wialon_username],
        widget=widgets.EmailInput(
            attrs={"class": default_css_class, "placeholder": "email@terminusgps.com"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=widgets.PasswordInput(attrs={"class": default_css_class}),
        validators=[validate_wialon_password],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=widgets.PasswordInput(attrs={"class": default_css_class}),
        validators=[validate_wialon_password],
    )


class TrackerAuthenticationForm(AuthenticationForm):
    default_css_class = "w-full block mt-2 mb-4 p-2 rounded-md text-black dark:bg-gray-800 dark:text-white"
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
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=32,
        widget=widgets.PasswordInput(attrs={"class": default_css_class}),
    )
