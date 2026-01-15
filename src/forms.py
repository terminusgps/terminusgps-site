from string import ascii_lowercase, ascii_uppercase, digits, punctuation

from django import forms
from django.conf import settings
from django.contrib.auth.forms import (
    AuthenticationForm,
    BaseUserCreationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.password_validation import (
    password_validators_help_texts,
)
from django.core.validators import validate_email
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

WIDGET_CSS_CLASS = getattr(
    settings,
    "WIDGET_CSS_CLASS",
    "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-valid:bg-green-50 user-valid:text-green-700 user-invalid:bg-red-50 user-invalid:text-red-600 group-has-[ul]:text-red-600 group-has-[ul]:bg-red-50",
)


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


class TerminusgpsRegistrationForm(BaseUserCreationForm):
    first_name = forms.CharField(
        max_length=64,
        help_text=_("Enter your first name."),
        widget=forms.widgets.TextInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "First",
                "autofocus": True,
                "autocomplete": True,
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=64,
        help_text=_("Enter your last name."),
        widget=forms.widgets.TextInput(
            attrs={
                "class": WIDGET_CSS_CLASS,
                "placeholder": "Last",
                "autocomplete": True,
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.password_help_texts = password_validators_help_texts()
        self.fields["username"].help_text = "Enter an email address."
        self.fields["username"].label = "Email Address"
        self.fields["username"].validators.append(validate_email)
        self.fields["password1"].validators.append(validate_wialon_password)
        self.fields["password2"].validators.append(validate_wialon_password)
        self.fields["username"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "email@terminusgps.com",
                "autocomplete": True,
                "autofocus": False,
                "inputmode": "email",
                "enterkeyhint": "next",
            }
        )
        self.fields["password1"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "done",
            }
        )


class TerminusgpsAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "email@terminusgps.com",
                "inputmode": "email",
                "enterkeyhint": "next",
                "autocomplete": "username email",
                "autofocus": True,
                "aria-required": "true",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "done",
                "aria-required": "true",
                "autocomplete": "current-password",
            }
        )


class TerminusgpsPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "next",
                "autocomplete": "current-password",
            }
        )
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "next",
                "autocomplete": "new-password",
            }
        )
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "done",
                "autocomplete": "new-password",
            }
        )
        self.password_help_texts = password_validators_help_texts()


class TerminusgpsPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["email"].label = _("Email Address")
        self.fields["email"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "email@terminusgps.com",
                "inputmode": "email",
                "enterkeyhint": "done",
                "autocomplete": True,
                "autofocus": True,
            }
        )


class TerminusgpsPasswordSetForm(SetPasswordForm):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "next",
                "autofocus": True,
            }
        )
        self.fields["new_password2"].widget.attrs.update(
            {
                "class": WIDGET_CSS_CLASS,
                "placeholder": "••••••••••••••••",
                "inputmode": "text",
                "enterkeyhint": "done",
            }
        )
        self.password_help_texts = password_validators_help_texts()
