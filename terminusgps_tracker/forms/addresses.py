from django import forms

from terminusgps_tracker.forms.fields import AddressField, AddressWidget


class CustomerShippingAddressCreationForm(forms.Form):
    first_name = forms.CharField(
        label="First Name",
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
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
        label="Set as your default shipping address?",
        required=False,
        initial=True,
    )
