from django import forms
from django.conf import settings

from terminusgps_tracker.forms.fields import AddressField


class CustomerShippingAddressCreateForm(forms.Form):
    first_name = forms.CharField(
        help_text="Please enter your first name.",
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
        help_text="Please enter your last name.",
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
        help_text="Please enter your phone number in the format:&nbsp;<em>555-555-5555</em>",
        label="Phone #",
        max_length=19,
        widget=forms.widgets.Input(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "555-555-5555",
                "maxlength": 32,
                "pattern": "\\d\\d\\d-\\d\\d\\d-\\d\\d\\d\\d",
                "inputmode": "tel",
                "type": "tel",
                "enterkeyhint": "next",
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
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
    )
