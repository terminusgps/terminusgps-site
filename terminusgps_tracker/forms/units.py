from django import forms
from terminusgps.wialon.validators import validate_imei_number


class CustomerWialonUnitCreationForm(forms.Form):
    name = forms.CharField(
        label="Unit Name",
        max_length=64,
        min_length=4,
        widget=forms.widgets.TextInput(
            attrs={
                "class": "p-2 w-full bg-white dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300 group-has-[.errorlist]:text-red-800 group-has-[.errorlist]:bg-red-100",
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
                "class": "p-2 w-full bg-white dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300 group-has-[.errorlist]:text-red-800 group-has-[.errorlist]:bg-red-100",
                "placeholder": "355197370065555",
                "inputmode": "numeric",
                "enterkeyhint": "done",
            }
        ),
    )
