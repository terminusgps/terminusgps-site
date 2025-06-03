from django import forms
from django.conf import settings

from terminusgps_tracker.forms.fields import AddressField


class CustomerShippingAddressCreationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "First",
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "Last",
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    phone = forms.CharField(
        help_text="Please enter your phone number in the format: 555-555-5555",
        label="Phone #",
        max_length=19,
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
    address = AddressField(
        label="Address", help_text="Please fill out a valid shipping address."
    )
    default = forms.BooleanField(
        help_text="Check this to set the new shipping address as your default.",
        label="Set as default shipping address?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
