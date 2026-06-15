from django import forms
from django.forms.widgets import EmailInput, TextInput
from phonenumber_field.widgets import RegionalPhoneNumberWidget

from . import models


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.ContactFormResponse
        fields = ["full_name", "email", "phone", "city", "state", "message"]
        widgets = {
            "full_name": TextInput(
                attrs={
                    "placeholder": "Your Name",
                    "autocomplete": "name",
                    "autofocus": "on",
                }
            ),
            "email": EmailInput(
                attrs={"placeholder": "email@domain.com", "autocomplete": "on"}
            ),
            "phone": RegionalPhoneNumberWidget(
                attrs={"placeholder": "+15555555555", "autocomplete": "tel"}
            ),
            "city": TextInput(
                attrs={
                    "placeholder": "Your City",
                    "autocomplete": "address-level2",
                }
            ),
            "state": TextInput(
                attrs={"placeholder": "Your State", "autocomplete": "on"}
            ),
        }
