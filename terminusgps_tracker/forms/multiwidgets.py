from typing import Any, Sequence
from datetime import date

from django import forms

from terminusgps_tracker.forms.widgets import TrackerTextInput


class ExpirationDateWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/expiration_date.html"

    def decompress(self, value: date | str) -> list:
        if value:
            if isinstance(value, date):
                return [value.month, value.year]
            elif isinstance(value, str):
                month, year = value.split("/")
                return [month, year]
        return [None, None]

    def value_from_datadict(self, data, files, name: str) -> list[Any]:
        month, year = super().value_from_datadict(data, files, name)
        return [f"{month}/{year}"]


class CreditCardWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/credit_card.html"

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["number", "expiry_month", "expiry_year", "ccv"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)


class AddressWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/address.html"

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)
