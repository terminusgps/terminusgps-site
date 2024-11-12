from typing import Any
from datetime import date
from django.urls import reverse_lazy

from django import forms


class CountryStateWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/country_state.html"
    attrs = {}

    def __init__(self, widgets, attrs: dict[str, str] | None = None, **kwargs) -> None:
        return super().__init__(widgets=widgets, attrs=attrs, **kwargs)

    def decompress(self, value: Any | None = None) -> list[Any]:
        if value:
            return [value[0], value[1]]
        return [None, None]


class ExpirationDateWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/expiration_date.html"
    attrs = {"hx-trigger": "keyup changed"}

    def __init__(self, widgets, attrs: dict[str, str] | None = None, **kwargs) -> None:
        if not attrs:
            attrs = self.attrs
        return super().__init__(widgets=widgets, attrs=attrs, **kwargs)

    def decompress(self, value: date | None = None) -> list:
        if value:
            return [value.month, value.year]
        return [None, None]

    def value_from_datadict(self, data, files, name: str) -> list[Any]:
        month, year = super().value_from_datadict(data, files, name)
        return [month, year]


class CreditCardWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/credit_card.html"
    attrs = {"hx-select": "#credit-card"}

    def __init__(self, widgets, attrs: dict[str, str] | None = None, **kwargs) -> None:
        if not attrs:
            attrs = self.attrs
        return super().__init__(widgets=widgets, attrs=attrs, **kwargs)

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["number", "expiry", "ccv"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)


class AddressWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/address.html"
    attrs = {"hx-trigger": "keyup changed", "hx-target": "#address-results"}

    def __init__(self, widgets, attrs: dict[str, str] | None = None, **kwargs) -> None:
        if not attrs:
            attrs = self.attrs
        return super().__init__(widgets=widgets, attrs=attrs, **kwargs)

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)
