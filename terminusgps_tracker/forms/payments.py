from django import forms

from terminusgps_tracker.forms.fields import AddressField, CreditCardField


class CustomerPaymentMethodCreateForm(forms.Form):
    first_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                "placeholder": "First Name",
                "maxlength": 64,
            }
        ),
    )
    last_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                "placeholder": "Last Name",
                "maxlength": 64,
            }
        ),
    )
    phone = forms.CharField(
        label="Phone #",
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                "placeholder": "555-555-5555",
                "maxlength": 32,
                "pattern": "\\d\\d\\d-\\d\\d\\d-\\d\\d\\d\\d",
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
