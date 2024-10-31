from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.forms import TerminusFormRenderer
from terminusgps_tracker.forms.widgets import (
    TerminusEmailInput,
    TerminusPasswordInput,
    TerminusTextInput,
)


class TerminusPasswordResetForm(PasswordResetForm):
    default_renderer = TerminusFormRenderer


class TerminusRegistrationForm(UserCreationForm):
    default_renderer = TerminusFormRenderer
    field_order = ["first_name", "last_name", "username", "password1", "password2"]

    first_name = forms.CharField(
        label="First Name", max_length=64, widget=TerminusTextInput()
    )
    last_name = forms.CharField(
        label="Last Name", max_length=64, widget=TerminusTextInput()
    )
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=TerminusEmailInput(),
        help_text=_("Please provide a valid email address for us to contact you at."),
    )
    password1 = forms.CharField(label="Password", widget=TerminusPasswordInput())
    password2 = forms.CharField(
        label="Confirm Password", widget=TerminusPasswordInput()
    )


class TerminusLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=TerminusEmailInput(),
        help_text=_("Your Terminus GPS account's email address."),
    )

    password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=32,
        widget=TerminusPasswordInput(),
        help_text=_("Your Terminus GPS account's password."),
    )
