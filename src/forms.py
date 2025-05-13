from typing import Any

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import validate_email
from django.forms import ValidationError, widgets
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.validators import validate_wialon_password


class TerminusgpsEmailSupportForm(forms.Form):
    email = forms.EmailField(
        label="Your Email Address",
        widget=forms.widgets.EmailInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "peter@terminusgps.com",
            }
        ),
    )
    subject = forms.CharField(
        label="Subject",
        max_length=1024,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "Subscription doesn't update...",
            }
        ),
    )
    message = forms.CharField(
        label="Message",
        max_length=2048,
        widget=forms.widgets.Textarea(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "I expected something to happen but something else happened instead...",
            }
        ),
    )


class TerminusgpsEmailVerificationForm(forms.Form):
    otp = forms.CharField(
        label="One-time Password (OTP)",
        max_length=6,
        widget=widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "inputmode": "text",
                "enterkeyhint": "done",
            }
        ),
    )


class TerminusgpsRegisterForm(UserCreationForm):
    field_order = ["first_name", "last_name", "username", "password1", "password2"]
    first_name = forms.CharField(
        help_text="Please enter your first name.",
        label="First Name",
        max_length=64,
        widget=widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "First",
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    last_name = forms.CharField(
        help_text="Please enter your last name.",
        label="Last Name",
        max_length=64,
        widget=widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "Last",
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    username = forms.CharField(
        help_text="Please enter a valid email address.",
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=widgets.EmailInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "email@terminusgps.com",
                "inputmode": "email",
                "enterkeyhint": "next",
            }
        ),
    )
    password1 = forms.CharField(
        help_text="<div class='flex-col'><h2>Password requirements:</h2><ul class='p-2 list-disc list-inside'><li>1 uppercase letter</li><li>1 lowercase letter</li><li>3 digits</li><li>1 special symbol</li><ul></div>",
        label="Password",
        widget=widgets.PasswordInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "minlength": 4,
                "maxlength": 64,
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
        validators=[validate_wialon_password],
    )
    password2 = forms.CharField(
        help_text="<div class='flex-col'><h2>Password requirements:</h2><ul class='p-2 list-disc list-inside'><li>1 uppercase letter</li><li>1 lowercase letter</li><li>3 digits</li><li>1 special symbol</li><ul></div>",
        label="Confirm Password",
        widget=widgets.PasswordInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "minlength": 4,
                "maxlength": 64,
                "inputmode": "text",
                "enterkeyhint": "done",
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


class TerminusgpsAuthenticationForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Couldn't find a user with those credentials. Please try again."
    }
    username = forms.CharField(
        help_text="Please enter the email address associated with your Terminus GPS account.",
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=widgets.EmailInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "email@terminusgps.com",
                "autofocus": True,
                "inputmode": "email",
                "enterkeyhint": "next",
            }
        ),
    )
    password = forms.CharField(
        help_text="Please enter the password associated with your Terminus GPS account.",
        min_length=8,
        max_length=64,
        widget=widgets.PasswordInput(
            attrs={"class": settings.DEFAULT_FIELD_CLASS, "enterkeyhint": "done"}
        ),
    )
