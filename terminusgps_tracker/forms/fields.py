from typing import Any, Collection

from django import forms


class CreditCardField(forms.MultiValueField):
    def compress(self, data_list: Collection) -> dict[str, Any]:
        data_keys = ["number", "expiry_month", "expiry_year", "ccv"]
        if data_list:
            return dict(zip(data_keys, data_list))
        return dict(zip(data_keys, [None] * len(data_keys)))


class AddressField(forms.MultiValueField):
    def compress(self, data_list: Collection) -> dict[str, Any]:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if data_list:
            return dict(zip(data_keys, data_list))
        return dict(zip(data_keys, [None] * len(data_keys)))
