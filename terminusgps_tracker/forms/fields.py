from typing import Any, Collection, Sequence

from django import forms

from terminusgps_tracker.forms.multiwidgets import AddressWidget
from terminusgps_tracker.forms.widgets import TrackerTextInput


class CreditCardField(forms.MultiValueField):
    def compress(self, data_list: Collection) -> dict[str, Any]:
        data_keys = ["number", "expiry_month", "expiry_year", "ccv"]
        if data_list:
            return dict(zip(data_keys, data_list))
        return dict(zip(data_keys, [None] * len(data_keys)))


class AddressField(forms.MultiValueField):
    def __init__(
        self, fields: Sequence[forms.Field], widget: forms.widgets.MultiWidget, **kwargs
    ) -> None:
        self.field_keys = ["street", "city", "state", "zip", "country", "phone"]
        print(fields)
        for field in fields:
            print(field.__dir__())
        print(widget)
        return super().__init__(fields=fields, widget=widget, **kwargs)

    def compress(self, data_list: Collection) -> dict[str, Any]:
        if data_list:
            return dict(zip(self.field_keys, data_list))
        return dict(zip(self.field_keys, [None] * len(self.field_keys)))
