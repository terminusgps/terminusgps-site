from django import forms

from terminusgps_tracker.forms.fields import AddressField


class CustomerShippingAddressCreateForm(forms.Form):
    default_field_class = "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"
    first_name = forms.CharField(
        label="First Name",
        widget=forms.widgets.TextInput(
            attrs={"class": default_field_class, "placeholder": "First"}
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.widgets.TextInput(
            attrs={"class": default_field_class, "placeholder": "Last"}
        ),
    )
    phone = forms.CharField(
        label="Phone #",
        widget=forms.widgets.TextInput(
            attrs={"class": default_field_class, "placeholder": "+15555555555"}
        ),
    )
    address = AddressField(label="Address")
    default = forms.BooleanField(
        label="Set as default shipping address?",
        required=False,
        initial=True,
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
    )
