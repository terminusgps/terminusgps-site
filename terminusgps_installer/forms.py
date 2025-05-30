from django import forms
from django.conf import settings
from terminusgps.wialon.validators import validate_imei_number

from terminusgps_installer.models import WialonAccount, WialonAssetCommand


class WialonAssetCommandExecutionForm(forms.Form):
    link_type = forms.ChoiceField(
        choices=WialonAssetCommand.WialonAssetCommandLinkType.choices,
        help_text="Please select a link type to execute the asset command with.",
        initial=WialonAssetCommand.WialonAssetCommandLinkType.AUTO,
        label="Link Type",
        required=False,
        widget=forms.widgets.Select(
            attrs={"class": settings.DEFAULT_FIELD_CLASS + " text-center"}
        ),
    )


class InstallJobCompletionForm(forms.Form):
    position_retrieved = forms.BooleanField(
        help_text="Please check this box if the unit's position was properly retrieved and rendered in a map.",
        initial=False,
        label="Unit position was retrieved.",
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
    )
    commands_executed = forms.BooleanField(
        help_text="Please check this box if test commands were properly executed by the unit.",
        initial=False,
        label="Unit commands were executed.",
        widget=forms.widgets.CheckboxInput(attrs={"class": "accent-terminus-red-700"}),
    )


class InstallJobCreationForm(forms.Form):
    imei_number = forms.CharField(
        label="IMEI #",
        help_text="Please enter the IMEI number found on the device.",
        max_length=19,
        validators=[validate_imei_number],
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "inputmode": "numeric",
                "placeholder": "869738060095555",
                "enterkeyhint": "next",
            }
        ),
    )
    account = forms.ModelChoiceField(
        label="Wialon Account",
        help_text="Please select a Wialon account to migrate the new asset into.",
        queryset=WialonAccount.objects.all(),
        widget=forms.widgets.Select(attrs={"class": settings.DEFAULT_FIELD_CLASS}),
    )
