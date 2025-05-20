from django import forms
from django.conf import settings

from terminusgps_tracker.forms.fields import AddressField, CreditCardField


class CustomerPaymentMethodCreateForm(forms.Form):
    first_name = forms.CharField(
        help_text="Please enter your first name.",
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
        help_text="Please enter your last name.",
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
        label="Credit Card",
        help_text="Please enter a valid credit card number and code.",
    )
    address = AddressField(
        label="Address", help_text="Please enter a valid shipping address."
    )
    default = forms.BooleanField(
        label="Set as default payment method?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
    )
    create_shipping_address = forms.BooleanField(
        label="Create shipping address from billing address?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
    )
