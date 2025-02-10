from django import forms
from django.utils import timezone

from terminusgps_tracker.forms.fields.expiration_date import (
    ExpirationDateField,
    ExpirationDateWidget,
)


class CreditCardWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/credit_card.html"

    def decompress(self, value: dict | None):
        if value is None:
            return [None] * len(self.widgets)

        return [value[0], value[1][0], value[1][1], value[2]]


class CreditCardField(forms.MultiValueField):
    widget = CreditCardWidget(
        widgets={
            "number": forms.widgets.NumberInput(
                attrs={
                    "class": "p-2 w-full border border-gray-600 rounded bg-gray-50 aria-[invalid]:bg-red-50 aria-[invalid]:text-red-700 aria-[invalid]:border-red-600",
                    "placeholder": "Card #",
                    "minlength": 16,
                    "maxlength": 19,
                }
            ),
            "expiry": ExpirationDateWidget(
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
            ),
            "ccv": forms.widgets.NumberInput(
                attrs={
                    "class": "p-2 w-full border border-gray-600 rounded bg-gray-50 aria-[invalid]:bg-red-50 aria-[invalid]:text-red-700 aria-[invalid]:border-red-600",
                    "placeholder": "CCV #",
                    "minlength": 3,
                    "maxlength": 4,
                }
            ),
        }
    )

    def __init__(self, **kwargs) -> None:
        fields = (forms.IntegerField(), ExpirationDateField(), forms.IntegerField())
        return super().__init__(fields, **kwargs)

    def compress(self, data_list):
        return {
            "number": data_list[0],
            "expiry": {"month": data_list[1][0], "year": data_list[1][1]},
            "ccv": data_list[2],
        }
