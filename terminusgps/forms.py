from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.validators import validate_email

from terminusgps_tracker.forms import TerminusFormRenderer
from terminusgps_tracker.forms.widgets import (
    TerminusEmailInput,
    TerminusPasswordInput,
    TerminusTextInput,
)


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
    )
    password1 = forms.CharField(label="Password", widget=TerminusPasswordInput())
    password2 = forms.CharField(
        label="Confirm Password", widget=TerminusPasswordInput()
    )
