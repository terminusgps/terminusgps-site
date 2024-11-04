from django import forms
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
)

from terminusgps_tracker.forms.renderer import TrackerFormRenderer
from terminusgps_tracker.forms.fields import CreditCardField, AddressField
from terminusgps_tracker.forms.widgets import (
    CreditCardWidget,
    AddressWidget,
    TrackerTextInput,
    TrackerEmailInput,
    TrackerPasswordInput,
    TrackerNumberInput,
)
from terminusgps_tracker.validators import (
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_username,
)


class TrackerPasswordResetForm(PasswordResetForm):
    default_renderer = TrackerFormRenderer
    email = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=TrackerEmailInput(attrs={"placeholder": "email@terminusgps.com"}),
        help_text=_(
            "Enter the email address associated with your Tracker GPS account."
        ),
    )


class TrackerRegistrationForm(UserCreationForm):
    field_order = ["first_name", "last_name", "username", "password1", "password2"]

    first_name = forms.CharField(
        label="First Name",
        max_length=64,
        widget=TrackerTextInput(attrs={"placeholder": "First"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=64,
        widget=TrackerTextInput(attrs={"placeholder": "Last"}),
    )
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email, validate_wialon_username],
        widget=TrackerEmailInput(attrs={"placeholder": "email@terminusgps.com"}),
        help_text=_("Please provide a valid email address for us to contact you at."),
    )
    password1 = forms.CharField(
        label="Password",
        widget=TrackerPasswordInput(),
        validators=[validate_wialon_password],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=TrackerPasswordInput(),
        validators=[validate_wialon_password],
    )


class TrackerAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=TrackerEmailInput(),
        help_text=_("Your Tracker GPS account's email address."),
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=32,
        widget=TrackerPasswordInput(),
        help_text=_("Your Tracker GPS account's password."),
    )


class AssetUploadForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=TrackerTextInput({"placeholder": "My Vehicle"}),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=TrackerNumberInput({"placeholder": "123412341234"}),
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
