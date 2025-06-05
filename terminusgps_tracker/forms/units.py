from django import forms
from django.conf import settings
from terminusgps.wialon.validators import validate_imei_number


class CustomerWialonUnitCreationForm(forms.Form):
    name = forms.CharField(
        help_text="Please enter a memorable name for your new unit.",
        label="Unit Name",
        max_length=64,
        min_length=4,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "My Vehicle",
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    imei = forms.CharField(
        help_text="Please enter the IMEI number found on your device.",
        label="IMEI #",
        max_length=19,
        min_length=12,
        validators=[validate_imei_number],
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "355197370065555",
                "inputmode": "numeric",
                "enterkeyhint": "done",
            }
        ),
    )
