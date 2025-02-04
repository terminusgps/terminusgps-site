from django import forms

from .fields import AddressField, CreditCardField


class PaymentMethodCreationForm(forms.Form):
    default = forms.BooleanField(initial=False, required=False)
    credit_card = CreditCardField()
    address = AddressField()
