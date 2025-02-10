from typing import Any
from django import forms
from django.utils import timezone


class ExpirationDateWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/expiration_date.html"

    def decompress(self, value: dict | None):
        if value is None:
            return [None] * len(self.widgets)

        return [value.get("month"), value.get("year")]


class ExpirationDateField(forms.MultiValueField):
    widget = ExpirationDateWidget(
        widgets={
            "month": forms.widgets.NumberInput(
                attrs={
                    "class": "p-2 w-full border border-gray-600 rounded bg-gray-50 aria-[invalid]:bg-red-50 aria-[invalid]:text-red-700 aria-[invalid]:border-red-600",
                    "placeholder": "MM",
                    "minlength": 2,
                    "maxlength": 2,
                    "min": 1,
                    "max": 12,
                }
            ),
            "year": forms.widgets.NumberInput(
                attrs={
                    "class": "p-2 w-full border border-gray-600 rounded bg-gray-50 aria-[invalid]:bg-red-50 aria-[invalid]:text-red-700 aria-[invalid]:border-red-600",
                    "placeholder": "YY",
                    "minlength": 2,
                    "maxlength": 2,
                    "min": int(f"{timezone.now():%y}"),
                    "max": 99,
                }
            ),
        }
    )

    def __init__(self, **kwargs) -> None:
        fields = (
            forms.IntegerField(label="Month", min_value=1, max_value=12),
            forms.IntegerField(
                label="Year", min_value=int(f"{timezone.now():%y}"), max_value=99
            ),
        )
        return super().__init__(fields, **kwargs)

    def clean(self, value):
        cleaned_data: dict[str, Any] = super().clean(value)
        month = cleaned_data.get("month")
        year = cleaned_data.get("year")
        if month and year:
            curr_year, curr_month = (
                int(f"{timezone.now():%y}"),
                int(f"{timezone.now():%m}"),
            )

            if year < curr_year or (year == curr_year and month < curr_month):
                raise forms.ValidationError("Expiration date cannot be in the past.")

    def compress(self, data_list) -> dict:
        return {"month": data_list[0], "year": data_list[1]}
