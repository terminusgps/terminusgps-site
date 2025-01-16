from django import forms
from django.forms import widgets

from terminusgps_tracker.models import TrackerAsset


class TrackerAssetUpdateForm(forms.ModelForm):
    class Meta:
        base_class = "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600"
        model = TrackerAsset
        fields = ("name", "imei_number")
        widgets = {
            "name": widgets.TextInput(
                attrs={"placeholder": "My Vehicle", "class": base_class}
            ),
            "imei_number": widgets.TextInput(
                attrs={
                    "placeholder": "IMEI #",
                    "class": base_class + " hover:cursor-not-allowed select-all",
                    "disabled": True,
                }
            ),
        }


class TrackerAssetCreateForm(forms.ModelForm):
    class Meta:
        model = TrackerAsset
        fields = ("name", "imei_number")
        widgets = {
            "name": widgets.TextInput(
                attrs={
                    "placeholder": "My Vehicle",
                    "class": "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600",
                }
            ),
            "imei_number": widgets.TextInput(
                attrs={
                    "placeholder": "IMEI #",
                    "class": "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600",
                }
            ),
        }


class AssetDeletionForm(forms.Form):
    asset = forms.ModelChoiceField(queryset=TrackerAsset.objects.all())
