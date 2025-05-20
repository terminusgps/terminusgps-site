from django import forms
from django.conf import settings
from django.core.validators import validate_image_file_extension
from django.urls import reverse_lazy


class VinNumberScanForm(forms.Form):
    image = forms.ImageField(
        label="Upload Image",
        allow_empty_file=False,
        validators=[validate_image_file_extension],
        widget=forms.widgets.FileInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "hx-preserve": True,
                "accept": "image/*",
                "capture": "environment",
                "enterkeyhint": "done",
            }
        ),
    )


class VinNumberScanConfirmForm(forms.Form):
    vin_number = forms.CharField(
        label="VIN #",
        max_length=17,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "AA0AAAA0AAA000000",
                "hx-get": reverse_lazy("installer:scan vin info"),
                "hx-trigger": "load, input changed delay:150ms",
                "hx-include": "this",
                "hx-target": "#vin-info",
                "hx-indicator": "#vin-info-spinner",
                "enterkeyhint": "enter",
                "inputmode": "text",
            }
        ),
    )


class UnitCreationForm(forms.Form):
    vin_number = forms.CharField(
        help_text="Please enter a VIN # for the vehicle you installed the device into.",
        label="VIN #",
        max_length=17,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "AA0AAAA0AAA000000",
                "enterkeyhint": "next",
                "inputmode": "text",
            }
        ),
    )
    imei_number = forms.CharField(
        help_text="Please enter an IMEI # for the device you installed into the vehicle.",
        label="IMEI #",
        max_length=19,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "867730050855555",
                "enterkeyhint": "next",
                "inputmode": "numeric",
            }
        ),
    )
    hw_type = forms.ChoiceField(
        help_text="Please select a hardware type for the device you installed.",
        label="Hardware Type",
        widget=forms.widgets.Select(
            attrs={"class": settings.DEFAULT_FIELD_CLASS, "enterkeyhint": "next"}
        ),
    )
    account_id = forms.CharField(
        help_text="Please enter a Wialon account # to migrate the new unit into.",
        label="Wialon Account #",
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "12345678",
                "enterkeyhint": "next",
                "inputmode": "numeric",
            }
        ),
    )
    verified = forms.BooleanField(
        label="By checking this box, you verify the information above accurately describes your install job.",
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
        initial=False,
    )
