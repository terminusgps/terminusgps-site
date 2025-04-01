from django import forms

from terminusgps_tracker.forms.fields import AddressField, CreditCardField


class CustomerPaymentMethodCreateForm(forms.Form):
    first_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full border border-gray-600 rounded bg-gray-50 aria-[invalid]:bg-red-50 aria-[invalid]:text-red-700 aria-[invalid]:border-red-600",
                "placeholder": "First Name",
                "maxlength": 64,
            }
        ),
    )
    last_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full border border-gray-600 rounded bg-gray-50 aria-[invalid]:bg-red-50 aria-[invalid]:text-red-700 aria-[invalid]:border-red-600",
                "placeholder": "Last Name",
                "maxlength": 64,
            }
        ),
    )
    phone = forms.CharField(
        label="Phone #",
        max_length=20,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full border border-gray-600 rounded bg-gray-50 aria-[invalid]:bg-red-50 aria-[invalid]:text-red-700 aria-[invalid]:border-red-600",
                "placeholder": "+15555555555",
                "maxlength": 20,
                "pattern": "\\+[0-9]+",
            }
        ),
    )
    credit_card = CreditCardField(label="Credit Card")
    address = AddressField(label="Address")
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
