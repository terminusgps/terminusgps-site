from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
)

from terminusgps_tracker.forms.renderer import TerminusFormRenderer
from terminusgps_tracker.forms.fields import CreditCardField, AddressField
from terminusgps_tracker.forms.widgets import (
    CreditCardWidget,
    AddressWidget,
    TerminusTextInput,
    TerminusEmailInput,
    TerminusPasswordInput,
    TerminusNumberInput,
)
from terminusgps_tracker.validators import (
    validate_django_username,
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_username,
)


class TerminusPasswordResetForm(PasswordResetForm):
    default_renderer = TerminusFormRenderer
    email = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=TerminusEmailInput(attrs={"placeholder": "email@terminusgps.com"}),
        help_text=_(
            "Enter the email address associated with your Terminus GPS account."
        ),
    )


class TerminusRegistrationForm(UserCreationForm):
    field_order = ["first_name", "last_name", "username", "password1", "password2"]

    first_name = forms.CharField(
        label="First Name",
        max_length=64,
        widget=TerminusTextInput(attrs={"placeholder": "First"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=64,
        widget=TerminusTextInput(attrs={"placeholder": "Last"}),
    )
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=TerminusEmailInput(attrs={"placeholder": "email@terminusgps.com"}),
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


class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        min_length=4,
        max_length=64,
        widget=TerminusTextInput({"placeholder": "First"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        min_length=4,
        max_length=64,
        widget=TerminusTextInput({"placeholder": "Last"}),
    )
    email = forms.EmailField(
        label="Email Address",
        validators=[validate_wialon_username, validate_django_username],
        min_length=4,
        max_length=512,
        widget=TerminusEmailInput({"placeholder": "email@terminusgps.com"}),
    )
    password1 = forms.CharField(
        label="Password",
        validators=[validate_wialon_password],
        min_length=4,
        max_length=32,
        widget=TerminusPasswordInput(),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=TerminusPasswordInput(),
        min_length=4,
        max_length=32,
    )

    def clean(self) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean()
        if cleaned_data:
            password = cleaned_data.get("password1")
            password_confirmation = cleaned_data.get("password2")

            if password and password_confirmation:
                if len(password) < 4:
                    error = ValidationError(
                        _("Password must be at least 4 chars in length. Got '%(len)s'"),
                        code="invalid",
                        params={"len": len(password)},
                    )
                    self.add_error("password1", error)
                    self.add_error("password2", error)
                elif password != password_confirmation:
                    error = ValidationError(
                        _("Passwords do not match."), code="invalid"
                    )
                    self.add_error("password1", error)
                    self.add_error("password2", error)
        return cleaned_data


class AssetUploadForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=TerminusTextInput({"placeholder": "My Vehicle"}),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=TerminusNumberInput({"placeholder": "123412341234"}),
        min_length=15,
        max_length=24,
    )


class CreditCardUploadForm(forms.Form):
    credit_card = CreditCardField(
        label="Credit Card",
        require_all_fields=True,
        fields=(
            forms.CharField(label="Card Number"),
            forms.CharField(label="Card Expiration"),
            forms.CharField(label="Card CCV #"),
        ),
        widget=CreditCardWidget(),
    )
    address = AddressField(
        label="Address",
        require_all_fields=False,
        fields=(
            forms.CharField(label="Street"),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Zip"),
            forms.ChoiceField(label="Country"),
            forms.CharField(label="Phone #"),
        ),
        widget=AddressWidget(),
    )
