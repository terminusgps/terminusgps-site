from django import forms

from terminusgps_tracker.forms.fields import AddressField


class CustomerShippingAddressCreationForm(forms.Form):
    address = AddressField()
    default = forms.BooleanField(
        label="Set as your default shipping address?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
