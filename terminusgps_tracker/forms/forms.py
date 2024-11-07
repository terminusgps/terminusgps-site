from django import forms
from django.core.validators import validate_email
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from terminusgps_tracker.forms.choices import CountryChoice, USStateChoice
from terminusgps_tracker.forms.fields import AddressField, CreditCardField
from terminusgps_tracker.forms.widgets import (
    TrackerTextInput,
    TrackerEmailInput,
    TrackerPasswordInput,
    TrackerNumberInput,
    TrackerSelectInput,
)
from terminusgps_tracker.forms.multiwidgets import (
    AddressWidget,
    CreditCardWidget,
    ExpirationDateWidget,
)
from terminusgps_tracker.models.subscription import TrackerSubscription
from terminusgps_tracker.validators import (
    validate_credit_card_number,
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_username,
)


class SubscriptionSelectForm(forms.Form):
    subscription = forms.ChoiceField(
        choices=TrackerSubscription.SubscriptionTier.choices,
        widget=TrackerSelectInput(attrs={"class": "bg-gray-500"}),
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
        widget=TrackerEmailInput(attrs={"placeholder": "email@terminusgps.com"}),
    )
    password = forms.CharField(
        label="Password", min_length=8, max_length=32, widget=TrackerPasswordInput()
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
        fields=(
            forms.CharField(label="Number", validators=[validate_credit_card_number]),
            forms.CharField(label="Expiration"),
            forms.CharField(label="CCV"),
        ),
        widget=CreditCardWidget(
            widgets={
                "number": TrackerTextInput(
                    attrs={
                        "placeholder": "Card #",
                        "minlength": "13",
                        "maxlength": "19",
                    }
                ),
                "expiry": ExpirationDateWidget(
                    widgets={
                        "month": TrackerTextInput(
                            attrs={"placeholder": "MM", "maxlength": "2"}
                        ),
                        "year": TrackerTextInput(
                            attrs={"placeholder": "YY", "maxlength": "2"}
                        ),
                    }
                ),
                "ccv": TrackerTextInput(
                    attrs={"placeholder": "CCV #", "minlength": "3", "maxlength": "4"}
                ),
            }
        ),
    )
    address = AddressField(
        label="Billing Address",
        fields=(
            forms.CharField(label="Street", max_length=64),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Zip"),
            forms.ChoiceField(label="Country"),
            forms.CharField(label="Phone #"),
        ),
        widget=AddressWidget(
            widgets={
                "street": TrackerTextInput(attrs={"placeholder": "Street"}),
                "city": TrackerTextInput(attrs={"placeholder": "City"}),
                "state": TrackerSelectInput(choices=USStateChoice.choices),
                "zip": TrackerTextInput(attrs={"placeholder": "Zip"}),
                "country": TrackerSelectInput(choices=CountryChoice.choices),
                "phone": TrackerTextInput(attrs={"placeholder": "Phone #"}),
            }
        ),
    )
