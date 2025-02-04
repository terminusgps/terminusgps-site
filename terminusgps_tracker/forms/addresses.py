from django import forms

from .fields import AddressField


class ShippingAddressCreationForm(forms.Form):
    default = forms.BooleanField(initial=False, required=False)
    address = AddressField()
