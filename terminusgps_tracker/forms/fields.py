from collections.abc import Collection
from typing import Any

from authorizenet.apicontractsv1 import creditCardType, customerAddressType
from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.forms import widgets as base_widgets
from django.utils import timezone

from terminusgps_tracker.validators import validate_credit_card_number


class AddressWidget(base_widgets.MultiWidget):
    template_name = "terminusgps_tracker/widgets/address.html"

    def __init__(self, widgets: Collection = (), *args, **kwargs) -> None:
        if not widgets:
            widgets = {
                "street": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "Street",
                        "maxlength": 128,
                    }
                ),
                "city": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "City",
                        "maxlength": 128,
                    }
                ),
                "state": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "State",
                        "maxlength": 64,
                    }
                ),
                "country": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "Country",
                        "maxlength": 64,
                    }
                ),
                "zip": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "Zip #",
                        "maxlength": 12,
                    }
                ),
            }
        super().__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value: Any):
        if value is None:
            return [None] * len(self.widgets)

        return {
            "street": value.address,
            "city": value.city,
            "state": value.state,
            "country": value.country,
            "zip": value.zip,
        }


class CreditCardWidget(base_widgets.MultiWidget):
    template_name = "terminusgps_tracker/widgets/credit_card.html"

    def __init__(self, widgets: Collection = (), *args, **kwargs) -> None:
        if not widgets:
            widgets = {
                "number": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "Card #",
                        "minlength": 16,
                        "maxlength": 19,
                    }
                ),
                "expiry_month": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "MM",
                        "minlength": 2,
                        "maxlength": 2,
                    }
                ),
                "expiry_year": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "YY",
                        "minlength": 2,
                        "maxlength": 2,
                    }
                ),
                "ccv": base_widgets.TextInput(
                    attrs={
                        "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300",
                        "placeholder": "CCV #",
                        "minlength": 3,
                        "maxlength": 4,
                    }
                ),
            }
        super().__init__(widgets=widgets, *args, **kwargs)

    def decompress(self, value: Any):
        if value is None:
            return [None] * len(self.widgets)

        expiry = value.cardExpiration.split("-")
        month, year = expiry[0], expiry[1][2:]
        return {
            "number": value.cardNumber,
            "expiry": {"month": month, "year": year},
            "ccv": value.cardCode,
        }


class AddressField(forms.MultiValueField):
    widget = AddressWidget

    def __init__(self, **kwargs) -> None:
        fields = (
            forms.CharField(label="Street"),
            forms.CharField(label="City"),
            forms.CharField(label="State"),
            forms.CharField(label="Country"),
            forms.CharField(label="Zip #"),
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list):
        return customerAddressType(
            **{
                "address": data_list[0],
                "city": data_list[1],
                "state": data_list[2],
                "country": data_list[3],
                "zip": data_list[4],
            }
        )


class CreditCardField(forms.MultiValueField):
    field_class: str = "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border dark:border-terminus-gray-300"
    widget = CreditCardWidget

    def __init__(self, **kwargs) -> None:
        fields = (
            forms.CharField(
                label="Card #",
                validators=[
                    MinLengthValidator(16),
                    MaxLengthValidator(19),
                    validate_credit_card_number,
                ],
            ),
            forms.IntegerField(
                label="Card Expiration Month", max_value=12, min_value=1
            ),
            forms.IntegerField(
                label="Card Expiration Year",
                max_value=99,
                min_value=int(f"{timezone.now():%y}"),  # Current year
            ),
            forms.CharField(
                label="Card CCV #",
                validators=[MinLengthValidator(3), MaxLengthValidator(4)],
            ),
        )
        return super().__init__(fields, **kwargs)

    def compress(self, data_list) -> creditCardType:
        return creditCardType(
            cardNumber=data_list[0],
            expirationDate=f"20{data_list[2]}-{data_list[1]:02d}",
            cardCode=data_list[3],
        )
