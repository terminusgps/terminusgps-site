from django import forms
from django.conf import settings
from django.core.validators import validate_image_file_extension


class VinNumberScanForm(forms.Form):
    image = forms.ImageField(
        label="Upload Image",
        allow_empty_file=False,
        validators=[validate_image_file_extension],
        widget=forms.widgets.FileInput(attrs={"class": settings.DEFAULT_FIELD_CLASS}),
    )


class UnitCreationForm(forms.Form):
    vin_number = forms.CharField(
        label="VIN #",
        max_length=17,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "AA0AAAA0AAA000000",
            }
        ),
    )
    imei_number = forms.CharField(
        label="IMEI #",
        max_length=19,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "867730050855555",
            }
        ),
    )
    account_id = forms.ChoiceField(
        label="Wialon Account",
        widget=forms.widgets.Select(attrs={"class": settings.DEFAULT_FIELD_CLASS}),
    )
