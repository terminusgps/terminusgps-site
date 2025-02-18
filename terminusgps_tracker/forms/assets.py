from django import forms
from django.forms import widgets

from terminusgps_tracker.models.assets import TrackerAsset


class TrackerAssetCreateForm(forms.ModelForm):
    class Meta:
        model = TrackerAsset
        fields = ("name",)
        widgets = {
            "name": widgets.TextInput(
                attrs={
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                    "placeholder": "My Vehicle",
                    "autocomplete": False,
                }
            )
        }

    imei_number = forms.CharField(
        max_length=25,
        min_length=9,
        widget=widgets.TextInput(
            attrs={
                "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                "placeholder": "IMEI #",
                "autocomplete": False,
            }
        ),
    )


class TrackerAssetUpdateForm(forms.ModelForm):
    class Meta:
        model = TrackerAsset
        fields = ("name",)
        widgets = {
            "name": widgets.TextInput(
                attrs={
                    "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                    "placeholder": "My Vehicle",
                    "autocomplete": False,
                }
            )
        }

    imei_number = forms.CharField(
        max_length=25,
        min_length=9,
        widget=widgets.TextInput(
            attrs={
                "class": "w-full block p-2 dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded",
                "placeholder": "IMEI #",
                "autocomplete": False,
            }
        ),
    )
