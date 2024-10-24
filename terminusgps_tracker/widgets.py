from typing import Any, Collection
from django import forms
from django.forms import widgets


class TextInput(widgets.TextInput):
    template_name = "terminusgps_tracker/forms/widgets/text.html"


class NumberInput(widgets.NumberInput):
    template_name = "terminusgps_tracker/forms/widgets/number.html"


class AddressField(forms.MultiValueField):
    def __init__(self, **kwargs) -> None:
        fields = (
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
            forms.CharField(),
        )
        widget = AddressWidget(
            widgets={
                "street": TextInput(),
                "city": TextInput(),
                "state": TextInput(),
                "zip": NumberInput(),
                "country": TextInput(),
                "phone": TextInput(),
            }
        )
        super().__init__(fields=fields, widget=widget, **kwargs)

    def compress(self, data_list: Collection | None) -> dict[str, Any]:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if data_list is not None:
            return dict(zip(data_keys, data_list))
        return dict(zip(data_keys, [None] * 6))


class AddressWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/address.html"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def decompress(self, value: dict[str, Any]) -> list[Any]:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * 6
