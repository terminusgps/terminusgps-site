from django import forms
from django.forms import widgets

from terminusgps_tracker.models import TrackerAsset


class TrackerAssetUpdateForm(forms.ModelForm):
    class Meta:
        model = TrackerAsset
        fields = ("name", "imei_number")
        widgets = {
            "name": widgets.TextInput(
                attrs={
                    "placeholder": "My Vehicle",
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                    "required": True,
                }
            ),
            "imei_number": widgets.TextInput(
                attrs={
                    "placeholder": "IMEI #",
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 hover:cursor-not-allowed select-all rounded",
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
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                }
            ),
            "imei_number": widgets.TextInput(
                attrs={
                    "placeholder": "IMEI #",
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                }
            ),
        }


class AssetDeletionForm(forms.Form):
    asset = forms.ModelChoiceField(queryset=TrackerAsset.objects.all())
