from django import forms
from django.conf import settings

from terminusgps_tracker.forms.fields import AddressField


class CustomerShippingAddressCreateForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        widget=forms.widgets.TextInput(
            attrs={"class": settings.DEFAULT_FIELD_CLASS, "placeholder": "First"}
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.widgets.TextInput(
            attrs={"class": settings.DEFAULT_FIELD_CLASS, "placeholder": "Last"}
        ),
    )
    phone = forms.CharField(
        label="Phone #",
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "555-555-5555",
                "maxlength": 32,
                "pattern": "\\d\\d\\d-\\d\\d\\d-\\d\\d\\d\\d",
            }
        ),
    )
    address = AddressField(label="Address")
    default = forms.BooleanField(
        label="Set as default shipping address?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
    )
