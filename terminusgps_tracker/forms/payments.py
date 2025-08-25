from django import forms
from django.conf import settings

from terminusgps_tracker.forms.fields import (
    AddressField,
    AddressWidget,
    CreditCardField,
    CreditCardWidget,
)


class CustomerPaymentMethodCreationForm(forms.Form):
    first_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "First Name",
                "maxlength": 64,
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "Last Name",
                "maxlength": 64,
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    phone = forms.CharField(
        help_text="Please enter your phone number in the format: 555-555-5555",
        label="Phone #",
        widget=forms.widgets.Input(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "enterkeyhint": "next",
                "inputmode": "text",
                "maxlength": 32,
                "pattern": "\\d\\d\\d-\\d\\d\\d-\\d\\d\\d\\d",
                "placeholder": "713-904-5555",
                "type": "tel",
            }
        ),
    )
    credit_card = CreditCardField(
        fields=(
            forms.CharField(label="Card #"),
            forms.DateField(label="Expiration Date"),
            forms.CharField(label="CCV #"),
        ),
        widget=CreditCardWidget(
            widgets={
                "number": forms.widgets.TextInput,
                "expiry": forms.widgets.DateInput(format="%d/%Y"),
                "ccv": forms.widgets.TextInput,
            }
        ),
    )
    address = AddressField(
        fields=(
            forms.CharField(label="First Name"),
            forms.CharField(label="Last Name"),
            forms.CharField(label="Phone #"),
            forms.CharField(label="Street"),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Zip"),
            forms.CharField(label="Country"),
        ),
        widget=AddressWidget(
            widgets={
                "first_name": forms.widgets.TextInput,
                "last_name": forms.widgets.TextInput,
                "phone_number": forms.widgets.TextInput,
                "street": forms.widgets.TextInput,
                "city": forms.widgets.TextInput,
                "state": forms.widgets.TextInput,
                "zip": forms.widgets.TextInput,
                "country": forms.widgets.TextInput,
            }
        ),
    )
    default = forms.BooleanField(
        label="Set as default payment method?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
    create_shipping_address = forms.BooleanField(
        label="Create shipping address from billing address?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
