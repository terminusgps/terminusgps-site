from django import forms
from django.conf import settings
from terminusgps.wialon.validators import (
    validate_imei_number,
    validate_vin_number,
)

from terminusgps_tracker.models import SubscriptionTier


class CustomerWialonUnitCreationForm(forms.Form):
    name = forms.CharField(
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
        error_messages={"invalid": "Couldn't find a device with this IMEI #."},
        help_text="Please enter the IMEI number found on your installed device.",
        label="IMEI #",
        max_length=19,
        min_length=5,
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
    vin = forms.CharField(
        help_text="Optionally enter the VIN # for the vehicle your device is installed in.",
        label="VIN #",
        max_length=17,
        required=False,
        validators=[validate_vin_number],
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "1HGCP2F40BA049468",
                "inputmode": "text",
                "enterkeyhint": "next",
            }
        ),
    )
    tier = forms.ModelChoiceField(
        initial=SubscriptionTier.objects.order_by("amount").first(),
        label="Subscription Tier",
        queryset=SubscriptionTier.objects.order_by("amount"),
        widget=forms.widgets.Select(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "enterkeyhint": "done",
            }
        ),
    )
