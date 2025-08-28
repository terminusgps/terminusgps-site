from django import forms

from terminusgps_tracker.forms.fields import AddressField, CreditCardField


class CustomerPaymentMethodCreationForm(forms.Form):
    address = AddressField()
    credit_card = CreditCardField()
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
