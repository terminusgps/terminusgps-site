from django import forms
from django.forms import widgets

from django.utils.translation import gettext_lazy as _


class ShippingAddressDeletionForm(forms.Form):
    address_id = forms.IntegerField(required=True, widget=widgets.HiddenInput())


class ShippingAddressSetDefaultForm(forms.Form):
    address_id = forms.IntegerField(required=True, widget=widgets.HiddenInput())


class ShippingAddressCreationForm(forms.Form):
    default_class = "w-full bg-white p-2 rounded-md dark:bg-gray-700"

    address_first_name = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "w-full bg-white p-2 rounded-md dark:bg-gray-700",
            }
        ),
    )
    address_last_name = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "w-full bg-white p-2 rounded-md dark:bg-gray-700",
            }
        ),
    )
    address_street = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={"placeholder": "Street", "class": default_class}
        ),
    )
    address_city = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(attrs={"placeholder": "City", "class": default_class}),
    )
    address_state = forms.CharField(
        max_length=32,
        widget=widgets.TextInput(
            attrs={"placeholder": "State", "class": default_class}
        ),
    )
    address_zip = forms.CharField(
        max_length=9,
        widget=widgets.TextInput(
            attrs={"placeholder": "ZIP #", "class": default_class}
        ),
    )
    address_country = forms.CharField(
        widget=widgets.Select(
            attrs={"class": default_class},
            choices=(
                ("USA", _("United States")),
                ("Mexico", _("Mexico")),
                ("Canada", _("Canada")),
            ),
        )
    )
    address_phone = forms.CharField(
        max_length=19,
        widget=widgets.TextInput(
            attrs={"placeholder": "Phone #", "class": default_class}
        ),
    )
    is_default = forms.BooleanField(
        initial=False,
        required=False,
        widget=widgets.CheckboxInput(attrs={"class": default_class}),
    )


class PaymentMethodDeletionForm(forms.Form):
    payment_id = forms.IntegerField(required=True, widget=widgets.HiddenInput())


class PaymentMethodSetDefaultForm(forms.Form):
    payment_id = forms.IntegerField(required=True, widget=widgets.HiddenInput())


class PaymentMethodCreationForm(forms.Form):
    default_class = "w-full bg-white p-2 rounded-md dark:bg-gray-700"

    credit_card_number = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(
            attrs={"placeholder": "Card #", "class": default_class}
        ),
    )
    credit_card_expiry_month = forms.CharField(
        min_length=2,
        max_length=2,
        widget=widgets.TextInput(attrs={"placeholder": "MM", "class": default_class}),
    )
    credit_card_expiry_year = forms.CharField(
        min_length=2,
        max_length=2,
        widget=widgets.TextInput(attrs={"placeholder": "YY", "class": default_class}),
    )
    credit_card_ccv = forms.CharField(
        min_length=3,
        max_length=4,
        widget=widgets.TextInput(
            attrs={"placeholder": "CCV #", "class": default_class}
        ),
    )

    address_first_name = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={"placeholder": "First Name", "class": default_class}
        ),
    )
    address_last_name = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={"placeholder": "Last Name", "class": default_class}
        ),
    )
    address_street = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={"placeholder": "Street", "class": default_class}
        ),
    )
    address_city = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(attrs={"placeholder": "City", "class": default_class}),
    )
    address_state = forms.CharField(
        max_length=32,
        widget=widgets.TextInput(
            attrs={"placeholder": "State", "class": default_class}
        ),
    )
    address_zip = forms.CharField(
        max_length=9,
        widget=widgets.TextInput(
            attrs={"placeholder": "ZIP #", "class": default_class}
        ),
    )
    address_country = forms.CharField(
        widget=widgets.Select(
            attrs={"class": default_class},
            choices=(
                ("USA", _("United States")),
                ("Mexico", _("Mexico")),
                ("Canada", _("Canada")),
            ),
        )
    )
    address_phone = forms.CharField(
        max_length=19,
        widget=widgets.TextInput(
            attrs={"placeholder": "Phone #", "class": default_class}
        ),
    )
    is_default = forms.BooleanField(
        initial=False,
        required=False,
        widget=widgets.CheckboxInput(
            attrs={"class": default_class + " accent-terminus-red-700"}
        ),
    )
    is_consenting = forms.BooleanField(
        initial=False,
        required=True,
        widget=widgets.CheckboxInput(
            attrs={"class": default_class + " accent-terminus-red-700"}
        ),
    )
