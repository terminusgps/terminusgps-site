from django import forms

from terminusgps_tracker.forms.fields import AddressField


class CustomerShippingAddressCreateForm(forms.Form):
    default_field_class = "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300"
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
            attrs={
                "class": default_field_class,
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
