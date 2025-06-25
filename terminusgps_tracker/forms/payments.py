import datetime

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.forms.fields import AddressField, CreditCardField


class CustomerPaymentMethodCreationForm(forms.Form):
    first_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "First Name",
                "maxlength": 64,
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=64,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "Last Name",
                "maxlength": 64,
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    phone = forms.CharField(
        help_text="Please enter your phone number in the format: 555-555-5555",
        label="Phone #",
        widget=forms.widgets.Input(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "enterkeyhint": "next",
                "inputmode": "text",
                "maxlength": 32,
                "pattern": "\\d\\d\\d-\\d\\d\\d-\\d\\d\\d\\d",
                "placeholder": "713-904-5555",
                "type": "tel",
            }
        ),
    )
    credit_card = CreditCardField(label="Credit Card")
    address = AddressField(label="Address")
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

    def clean_credit_card(self):
        cc = self.cleaned_data.get("credit_card")

        if cc:
            expiry_date = datetime.datetime.strptime(
                str(cc.expirationDate), "%Y-%m"
            )
            if not expiry_date >= datetime.datetime.now():
                raise ValidationError(
                    _(
                        "Expiration date cannot be in the past, got '%(expiry)s'."
                    ),
                    code="invalid",
                    params={"expiry": str(cc.expirationDate)},
                )
            return cc
