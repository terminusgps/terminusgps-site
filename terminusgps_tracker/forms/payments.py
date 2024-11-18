from django import forms
from django.forms import widgets

from django.utils.translation import gettext_lazy as _
from terminusgps_tracker.validators import validate_credit_card_number


class PaymentMethodCreationForm(forms.Form):
    credit_card_number = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(
            attrs={"placeholder": "Card #", "class": "w-full bg-white p-2 rounded-md"}
        ),
        validators=[validate_credit_card_number],
    )
    credit_card_expiry_month = forms.CharField(
        min_length=2,
        max_length=2,
        widget=widgets.TextInput(
            attrs={"placeholder": "MM", "class": "w-full bg-white p-2 rounded-md"}
        ),
    )
    credit_card_expiry_year = forms.CharField(
        min_length=2,
        max_length=2,
        widget=widgets.TextInput(
            attrs={"placeholder": "YY", "class": "w-full bg-white p-2 rounded-md"}
        ),
    )
    credit_card_ccv = forms.CharField(
        min_length=3,
        max_length=4,
        widget=widgets.TextInput(
            attrs={"placeholder": "CCV #", "class": "w-full bg-white p-2 rounded-md"}
        ),
    )

    address_street = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={"placeholder": "Street", "class": "w-full bg-white p-2 rounded-md"}
        ),
    )
    address_city = forms.CharField(
        max_length=64,
        widget=widgets.TextInput(
            attrs={"placeholder": "City", "class": "w-full bg-white p-2 rounded-md"}
        ),
    )
    address_state = forms.CharField(
        max_length=32,
        widget=widgets.TextInput(
            attrs={"placeholder": "State", "class": "w-full bg-white p-2 rounded-md"}
        ),
    )
    address_zip = forms.CharField(
        max_length=9,
        widget=widgets.TextInput(
            attrs={"placeholder": "ZIP #", "class": "w-full bg-white p-2 rounded-md"}
        ),
    )
    address_country = forms.CharField(
        widget=widgets.Select(
            attrs={"class": "w-full bg-white p-2 rounded-md"},
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
            attrs={"placeholder": "Phone #", "class": "w-full bg-white rounded-md p-2"}
        ),
    )
    is_default = forms.BooleanField(
        initial=False,
        widget=widgets.CheckboxInput(
            attrs={"class": "bg-white rounded-md accent-terminus-red-700"}
        ),
    )
    is_consenting = forms.BooleanField(
        initial=False,
        required=True,
        widget=widgets.CheckboxInput(
            attrs={"class": "bg-white rounded-md accent-terminus-red-700"}
        ),
    )


class PaymentMethodDeletionForm(forms.Form): ...
